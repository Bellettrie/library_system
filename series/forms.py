from django.forms import Widget
from django.template import loader

from django.conf import settings

from django.forms import ModelForm

from series.models import SeriesV2


class SeriesWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('series/search_field.html')
        default_options = SeriesV2.objects.filter(work_id=value)
        default_option = None
        if len(default_options) == 1:
            default_option = default_options[0]
        return template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL, "default": default_option})


NAMED_TRANSLATED_LIST = ['title', 'sub_title', 'article', 'original_title', 'original_subtitle', 'original_article',
                         'language', 'original_language']


class SeriesForm(ModelForm):
    class Meta:
        model = SeriesV2
        fields = ['location']
