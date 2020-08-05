from django.forms import Widget
from django.template import loader

from creators.models import Creator

from django.conf import settings

from series.models import Series


class SeriesWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('series_search_field.html')
        default_options = Series.objects.filter(pk=value)
        default_option = None
        if len(default_options) == 1:
            default_option = default_options[0]
        return template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL, "default": default_option})
