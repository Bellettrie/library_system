from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory, Widget
from django.forms.widgets import TextInput
from django.template import loader
from django.urls import reverse
from django.utils.safestring import mark_safe

from creators.forms import CreatorWidget
from series.forms import SeriesWidget
from works.models import ItemState, Item, CreatorToWork, Work, WorkRelation


class SimpleWorkSearch(forms.Form):
    name = forms.CharField(required=False)


class ItemStateCreateForm(ModelForm):
    class Meta:
        model = ItemState
        fields = ['type', 'reason']


class ItemCreateForm(ModelForm):
    class Meta:
        model = Item
        fields = ['book_code',
                  'book_code_extension',
                  'isbn10',
                  'isbn13',
                  'pages',
                  'hidden',
                  'comment',
                  'publication_year',
                  'bought_date',
                  'last_seen',
                  'location',
                  'bought_date',
                  ]
        widgets = {
            'bought_date': forms.DateInput(attrs={'class': 'datepicker'})
        }


NAMED_TRANSLATED_LIST = ['title', 'article', 'sub_title', 'language', 'original_title', 'original_article',
                         'original_subtitle', 'original_language']


class WorkForm(ModelForm):
    class Meta:
        model = Work
        z_fields = [
            'hidden',
            'sorting',
            'comment',
            'internal_comment',
            'date_added'
        ]
        widgets = {
            'date_added': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'})
        }
        fields = []
        for i in NAMED_TRANSLATED_LIST:
            fields.append(i)
        for field in z_fields:
            fields.append(field)


class SubWorkForm(ModelForm):
    class Meta:
        model = Work
        z_fields = [
            'hidden',
            'sorting',
            'comment',
            'internal_comment',
            'date_added'
        ]
        widgets = {
            'date_added': forms.DateInput(attrs={'class': 'datepicker'})
        }
        fields = []
        for i in NAMED_TRANSLATED_LIST:
            fields.append(i)
        for field in z_fields:
            fields.append(field)


class LocationChangeForm(ModelForm):
    book_code = forms.CharField(required=True)
    book_code_extension = forms.CharField(required=False)

    class Meta:
        model = Item
        fields = ['location']


CreatorToWorkFormSet = inlineformset_factory(Work, CreatorToWork, can_delete=True, fields=['creator', 'number', 'role'],
                                             widgets={'creator': CreatorWidget})


class WorkFindWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('works/work_select.html')

        default_options = Work.objects.filter(pk=value)
        default_option = None
        if len(default_options) == 1:
            default_option = default_options[0]
        return template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL, "default": default_option})


class ReadOnlyText(TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        work = Work.objects.filter(pk=value)
        if len(work) > 0:
            title = work[0].get_description_title()
        else:
            title = ""
        return super(ReadOnlyText, self).render(name, title, attrs, renderer)


relation_choices = [
    (1, 'Is Subwork Of'),
    (2, "Is Part of Series"),
    (3, "Is Part of Secondary Series"),
    # (4, "Is Translation of"),
]


def clean_rel_form(rel_form):
    kind = rel_form.cleaned_data["relation_kind"]
    from_work = rel_form.cleaned_data["from_work"]
    to_work = rel_form.cleaned_data["to_work"]
    if from_work.id == to_work.id:
        raise ValidationError("❗From work is to work, that's not allowed")

    relation_index = rel_form.cleaned_data["relation_index"]
    wr = WorkRelation.objects.filter(to_work=to_work, relation_index=relation_index, relation_kind=kind).exclude(
        from_work=from_work)

    if len(wr) > 0:
        raise ValidationError(
            "❗Another relation exists for {to_work.title} for index {index}, which hits.".format(to_work=to_work,
                                                                                                 index=relation_index))

    if kind == WorkRelation.RelationKind.sub_work_of:
        if from_work.as_series():
            raise ValidationError(
                "❗{from_work.title} is a series, so cannot be a subwork.".format(from_work=from_work))
        if to_work.as_series():
            raise ValidationError(
                "❗{to_work.title} is a series, so cannot be the top of a subwork.".format(to_work=to_work))
        if relation_index is None:
            raise ValidationError("Subwork relationship needs a relation index.")

    if kind == WorkRelation.RelationKind.part_of_series:

        st = set()
        st.add(to_work.id)
        nw = to_work
        while True:
            ser = nw.part_of_series()
            if ser is None:
                break
            if ser.to_work_id in st:
                raise ValidationError(
                    "❗{to_work.title} would now be part of a series loop, loops make the system dizzy.".format(to_work=ser.to_work))
            if ser.from_work_id in st:
                raise ValidationError(
                    "❗{to_work.title} would now be part of a series loop, loops make the system dizzy.".format(to_work=ser.from_work))
            nw = ser.to_work
            st.add(nw.id)

        if not to_work.as_series():
            raise ValidationError(
                "❗{to_work.title} is a not series, so this relation is impossible.".format(to_work=to_work))

        wr = WorkRelation.objects.filter(from_work=from_work, relation_kind=kind).exclude(relation_index=relation_index)

        if len(wr) > 0:
            raise ValidationError(
                "❗One work can be part of only one series. {from_work.get_title} is already part of a series.".format(
                    from_work=from_work))
        if relation_index is None:
            raise ValidationError("Series needs a relation index.")

    if kind == WorkRelation.RelationKind.part_of_secondary_series:
        if not to_work.as_series():
            raise ValidationError(
                "❗{to_work.title} is a not series, so this relation is impossible.".format(to_work=to_work))
        if relation_index is None:
            raise ValidationError("Secondary Series needs a relation index.")

    if kind == WorkRelation.RelationKind.translation_of:
        if (not not to_work.as_series()) != (not not from_work.as_series()):
            raise ValidationError(
                "❗{to_work.title} and {from_work.title} need to either both be a series, or both not be.".format(
                    to_work=to_work, from_work=from_work))
        if relation_index is not None:
            raise ValidationError("Subwork relationship needs a relation index.")


class RelationForm(ModelForm):
    class Meta:
        model = WorkRelation
        fields = ['from_work', 'relation_kind', 'to_work', 'relation_index', 'relation_index_label']
        widgets = {'to_work': WorkFindWidget, 'from_work': ReadOnlyText}

    def clean(self):
        super(RelationForm, self).clean()
        clean_rel_form(self)

    def render(self, *args, **kwargs):
        super(RelationForm, self).render(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(RelationForm, self).__init__(*args, **kwargs)
        self.fields["from_work"].disabled = True
        if self.instance.pk is None:
            url = reverse('works.relation.edit.rev', args=(self.instance.from_work.id, self.instance.id or -1))
            self.fields['relation_kind'].label = mark_safe("Relation <a class=\"text-2xl\" href=\"" + url + "\">⇅</a>")
        else:
            self.fields['relation_kind'].label = "Relation"
            self.fields['relation_kind'].disabled = True
            self.fields['to_work'].disabled = True
            self.fields['to_work'].widget = ReadOnlyText()
        self.fields['relation_kind'].choices = relation_choices


class RelationFormRev(ModelForm):
    class Meta:
        model = WorkRelation
        fields = ['from_work', 'relation_kind', 'to_work', 'relation_index', 'relation_index_label']
        widgets = {'from_work': WorkFindWidget, 'to_work': ReadOnlyText}

    def clean(self):
        super(RelationFormRev, self).clean()
        clean_rel_form(self)

    def __init__(self, *args, **kwargs):
        super(RelationFormRev, self).__init__(*args, **kwargs)
        self.fields["to_work"].disabled = True
        if self.instance.pk is None:
            url = reverse('works.relation.edit', args=(self.instance.to_work.id, self.instance.id or -1))
            self.fields['relation_kind'].label = mark_safe("Relation <a class=\"text-2xl\" href=\"" + url + "\">⇅</a>")
        else:
            self.fields['relation_kind'].label = "Relation"
            self.fields['relation_kind'].disabled = True
            self.fields['from_work'].disabled = True
            self.fields['from_work'].widget = ReadOnlyText()

        self.fields['relation_kind'].choices = relation_choices
