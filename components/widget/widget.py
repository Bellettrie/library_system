from django.urls import reverse
from django_components import Component, register, types


@register("widget/widget_base")
class BaseWidget(Component):
    def get_context_data(self, root_class_tags=""):

        return {
            "root_class_tags":root_class_tags,
        }
    template_name = "widget/widget.html"
