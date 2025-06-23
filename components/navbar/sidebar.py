from django_components import Component, register

from bellettrie_library_system import settings
from components.navbar.menus.menu import right_limited_menu, sidebar, mobile_menu


@register("nav.sidebar.Sidebar")
class Sidebar(Component):
    template_name = "navbar/sidebar.html"

    # The sidebar always shows its own menu, and shows the mobile_only entries only if the sidebar switches to the foldout mode.
    def get_context_data(self, perms):

        return {
            "items": right_limited_menu(sidebar, perms),
            "mobile_items": right_limited_menu(mobile_menu, perms),
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }
