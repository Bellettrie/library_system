from django_components import Component, register

from bellettrie_library_system import settings
from components.navbar.menu import menu_with_only_right_permissions, footer


@register("navbar.footer.Footer")
class Footer(Component):
    def get_context_data(self, perms):
        return {
            "footer_items": menu_with_only_right_permissions(footer, perms),
        }

    template_name = "navbar/footer.html"
