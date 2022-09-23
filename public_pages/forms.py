from django import forms
from django.conf import settings
from django.forms import ModelForm, Widget
from django.template import loader

from members.models import Member
from public_pages.models import PublicPage, FileUpload


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['name', 'file']


class PageTextWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('public_pages/page_edit_widget.html')
        return template.render({'name': name, 'value': value, 'BASE_UR': settings.BASE_URL})


class PageEditForm(ModelForm):
    class Meta:
        model = PublicPage
        fields = ['name',
                  'title',
                  'group',
                  'text',
                  "show_title",
                  "only_for_logged_in",
                  ]
        labels = {'name': 'Name',
                  'title': 'Title',
                  'text': 'Text',
                  'group': 'Group',
                  'show_title': 'Show Title?',
                  "only_for_logged_in": "Only for logged in users?",
                  },
        widgets = {'text': PageTextWidget}
