from django.forms import Form
from django_components import Component, register


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
