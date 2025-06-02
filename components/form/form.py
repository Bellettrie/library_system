from typing import List

from django.forms import Field, Form
from django.urls import reverse
from django_components import Component, register, types


@register("form.Form")
class Form(Component):
    template_name = "form/form.html"

    def get_context_data(self, form: Form):
        return {
            "form": form,
        }


@register("form.Compact")
class Compact(Component):
    template_name = "form/compact.html"

    def get_context_data(self, form: Form):
        return {
            "form": form,
        }


@register("form.Smol")
class Smol(Component):
    template_name = "form/smol.html"

    def get_context_data(self, form: Form):
        return {
            "form": form,
        }
