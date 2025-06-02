from typing import Optional, Any

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types
from django_components.component import DataType

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("footer.Footer")
class Footer(Component):
    def get_context_data(self):
        return {
            "standard_page_group": settings.STANDARD_PAGE_GROUP,
        }
    template_name = "footer.html"
