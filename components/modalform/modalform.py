from typing import Optional

from django.template.context import Context

from django.urls import reverse
from django_components import Component, register, types

from bellettrie_library_system import settings
from bellettrie_library_system.base_settings import GET_MENU


@register("modalform.ModalForm")
class ModalForm(Component):
    template_name = "modalform/modalform.html"
    def get_context_data(self, form_path="#", with_cancel=False, form_button_name="Submit", button_type="primary"):
        return {
            "form_path": form_path,
            "with_cancel": with_cancel,
            "form_button_name": form_button_name,
            "button_type": button_type,
        }

