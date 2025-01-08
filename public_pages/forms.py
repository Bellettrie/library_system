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
                  "show_title",
                  ]
        labels = {
                  "only_for_logged_in": "Only for logged in users?",
                  "only_for_current_members": "Only for current members?",
                  "limited_to_committees": "Limit to these committees",
                  },


class PageAccessForm(ModelForm):
    class Meta:
        model = PublicPage
        fields = [
            "only_for_logged_in",
            "only_for_current_members",
            "limited_to_committees",
        ]
        labels = {
                  "only_for_logged_in": "Only for logged in users?",
                  "only_for_current_members": "Only for current members?",
                  "limited_to_committees": "Limit to these committees",
                  },


class EditForm(ModelForm):
    class Meta:
        model = PublicPage
        fields = [
            'text',

        ]

        widgets = {'text': PageTextWidget}
