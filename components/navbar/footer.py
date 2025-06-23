from django_components import Component, register

from bellettrie_library_system import settings
from components.navbar.menu import right_limited_menu, footer


@register("navbar.footer.Footer")
class Footer(Component):
    def get_context_data(self, perms):
        return {
            "footer_items": right_limited_menu(footer, perms),
        }

    template_name = "navbar/footer.html"
