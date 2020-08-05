from django import forms
from django.forms import ModelForm, inlineformset_factory

from creators.forms import CreatorWidget
from works.models import ItemState, Item, Publication, CreatorToWork
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


class PublicationCreateForm(ModelForm):
    class Meta:
        model = Publication
        fields = ['book_code',
                  'title',
                  'sub_title',
                  'hidden',
                  ]


class CreatorToWorkForm(ModelForm):
    class Meta:
        model = CreatorToWork
        fields = ['creator',
                  'number',
                  'role'
                  ]


CreatorToWorkFormSet = inlineformset_factory(Publication, CreatorToWork, can_delete=True, fields=['creator', 'number', 'role'], widgets={'creator': CreatorWidget})
