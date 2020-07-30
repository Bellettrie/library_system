from django import forms
from django.forms import ModelForm

from works.models import ItemState, Item


class SimpleWorkSearch(forms.Form):
    name = forms.CharField(required=False)


class ItemStateCreateForm(ModelForm):
    class Meta:
        model = ItemState
        fields = ['type', 'reason']


class ItemCreateForm(ModelForm):
    class Meta:
        model = Item
        fields = ['signature',
                  'signature_extension',
                  'isbn10',
                  'isbn13',
                  'pages',
                  'hidden',
                  'comment',
                  'publication_year',
                  'bought_date',
                  'last_seen']
