from django_components import Component, register

from public_pages.renderer.helpers import url_conv


@register("tile.Tile")
class Tile(Component):
    def get_context_data(self, root_class_tags="", with_standard_flex=True, figure_url=None, figure_alt=None):
        return {
            "figure_url": url_conv(figure_url),
            "figure_alt": figure_alt or "picture",
            "with_standard_flex": with_standard_flex,
            "root_class_tags": root_class_tags,
        }

    template_name = "tile/tile.html"


@register("tile.Footer")
class Footer(Component):
    def get_context_data(self, root_class_tags=""):
        return {
            "root_class_tags": root_class_tags,
        }

    template_name = "tile/footer.html"
