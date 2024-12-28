from django.urls import reverse
from django_components import Component, register, types


@register("tile/tile")
class BaseTile(Component):
    def get_context_data(self, root_class_tags=""):
        return {
            "root_class_tags": root_class_tags,
        }

    template_name = "tile/tile.html"

@register("tile/footer")
class TileFooter(Component):
    def get_context_data(self, root_class_tags=""):
        return {
            "root_class_tags": root_class_tags,
        }

    template_name = "tile/footer.html"
