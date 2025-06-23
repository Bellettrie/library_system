from django_components import Component, register

from bellettrie_library_system import settings
from components.navbar.menu import right_limited_menu, sidebar, top_bar


@register("navbar.sidebar.Sidebar")
class Sidebar(Component):
    template_name = "navbar/sidebar.html"

    # The sidebar always shows its own menu, and shows the mobile_only entries only if the sidebar switches to the foldout mode.
    def get_context_data(self, perms):

        return {
            "hide_sidebar_xl": len(right_limited_menu(sidebar, perms)) == 0,
            "sidebar_items": right_limited_menu(sidebar, perms),
            "top_bar": right_limited_menu(top_bar, perms),
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }
