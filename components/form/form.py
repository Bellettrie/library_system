from typing import List

from django.forms import Field, Form
from django.urls import reverse
from django_components import Component, register, types


@register("form/form")
class Form(Component):
    template_name = "form/form.html"

    def get_context_data(self, form:Form):
        return {
            "form": form,
        }

@register("form/compact")
class CompactForm(Component):
    template_name = "form/compact.html"

    def get_context_data(self, form:Form):

        return {
            "form": form,
        }
