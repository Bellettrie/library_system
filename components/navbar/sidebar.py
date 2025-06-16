from django_components import Component, register

from bellettrie_library_system import settings


@register("nav.sidebar.Sidebar")
class Sidebar(Component):
    template_name = "navbar/sidebar.html"

    # The sidebar always shows its own menu, and shows the mobile_only entries only if the sidebar switches to the foldout mode.
    def get_context_data(self, menu=None, mobile_only=None):
        if menu is None:
            menu = []

        return {
            "items": menu,
            "mobile_items": mobile_only,
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }
