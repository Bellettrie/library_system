# In a file called [project root]/components/calendar/calendar.py
from typing import Optional

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("footer.Footer")
class Footer(Component):
    template_name = "footer.html"