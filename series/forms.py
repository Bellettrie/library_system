from django.forms import Widget
from django.template import loader

from creators.forms import CreatorWidget
from creators.models import Creator

from django.conf import settings

from series.models import Series, CreatorToSeries
from django.forms import ModelForm, inlineformset_factory


class SeriesWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template('series/search_field.html')
        default_options = Series.objects.filter(pk=value)
        default_option = None
        if len(default_options) == 1:
            default_option = default_options[0]
        return template.render({'name': name, 'value': value, 'BASE_URL': settings.BASE_URL, "default": default_option})


NAMED_TRANSLATED_LIST = ['title', 'sub_title', 'article', 'original_title', 'original_subtitle', 'original_article', 'language', 'original_language']


class SeriesCreateForm(ModelForm):
    class Meta:
        model = Series
        fields = ['book_code', 'location', 'title', 'sub_title', 'article', 'original_title', 'original_subtitle', 'original_article', 'language', 'original_language', 'part_of_series', 'number',
                  'display_number']
        widgets = {'part_of_series': SeriesWidget}


CreatorToSeriesFormSet = inlineformset_factory(Series, CreatorToSeries, can_delete=True, fields=['creator', 'number', 'role'], widgets={'creator': CreatorWidget})
