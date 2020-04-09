from django import forms


class SimpleWorkSearch(forms.Form):
    name = forms.CharField(required=False)
