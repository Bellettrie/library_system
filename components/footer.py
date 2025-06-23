from django_components import Component, register

from bellettrie_library_system import settings


@register("footer.Footer")
class Footer(Component):
    def get_context_data(self):
        return {
            "standard_page_group": settings.STANDARD_PAGE_GROUP,
        }

    template_name = "footer.html"
