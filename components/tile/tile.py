from django.urls import reverse
from django_components import Component, register, types


@register("tile/tile")
class BaseWidget(Component):
    def get_context_data(self, root_class_tags=""):

        return {
            "root_class_tags":root_class_tags,
        }
    template_name = "tile/tile.html"
