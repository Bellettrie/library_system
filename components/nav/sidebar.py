# In a file called [project root]/components/calendar/calendar.py
from typing import Optional

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("nav.sidebar.Sidebar")
class Sidebar(Component):
    template_name = "nav/sidebar.html"

    # This component takes one parameter, a date string to show in the template
    def get_context_data(self, menu=None):
        if menu is None:
            menu = []

        return {
            "items": menu,
            "logo_debug": settings.UPSIDE_DOWN,
            "logo_name": settings.LIBRARY_NAME,
            "logo_image": settings.LIBRARY_IMAGE_URL,
        }

    class Media:
        css = "nav/navbar.css"
