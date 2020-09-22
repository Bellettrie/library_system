from django.forms import Widget, ModelForm, inlineformset_factory, TextInput
from django.template import loader

from creators.models import Creator, CreatorLocationNumber

from django.conf import settings


class CreatorWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('creator_search_field.html')
        default_options = Creator.objects.filter(pk=value)
        default_option = None
        if len(default_options) == 1:
            default_option = default_options[0]
        return template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL, "default": default_option})


class EditForm(ModelForm):
    class Meta:
        model = Creator
        fields = ['name',
                  'given_names',
                  'is_alias_of'

                  ]
        labels = {'name': 'Name',
                  'given_names': 'Given Names',
                  'is_alias_of': 'Is Alias Of'
                  }
        widgets = {
            'is_alias_of': CreatorWidget,
        }


class TurboWidget(TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('creator_book_code_lookup.html')

        return super().render(name=name, value=value, attrs=attrs) + template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL})


CreatorLocationNumberFormset = inlineformset_factory(Creator, CreatorLocationNumber, can_delete=True, fields=['location', 'letter', 'number'], widgets={'number': TurboWidget})
