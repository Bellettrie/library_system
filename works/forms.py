from django import forms
from django.forms import ModelForm, inlineformset_factory

from creators.forms import CreatorWidget
from series.forms import SeriesWidget
from series.models import WorkInSeries
from works.models import ItemState, Item, Publication, CreatorToWork, Work
from django.forms import formset_factory


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
                  'last_seen']


NAMED_TRANSLATED_LIST = ['title', 'sub_title', 'article', 'original_title', 'original_subtitle', 'original_article', 'language', 'original_language']


class PublicationCreateForm(ModelForm):
    class Meta:
        model = Publication
        z_fields = [
            'hidden',
            'sorting',
            'comment',
            'internal_comment',
            'date_added'
        ]
        fields = ['book_code']
        for i in NAMED_TRANSLATED_LIST:
            fields.append(i)
        for field in z_fields:
            fields.append(field)


CreatorToWorkFormSet = inlineformset_factory(Work, CreatorToWork, can_delete=True, fields=['creator', 'number', 'role'], widgets={'creator': CreatorWidget})
SeriesToWorkFomSet = inlineformset_factory(Work, WorkInSeries, can_delete=True, fields=['part_of_series', 'number', 'is_primary'], widgets={'part_of_series': SeriesWidget})
