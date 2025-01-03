from django.urls import reverse
from django_components import Component, register, types


@register("inputs/text")
class TextInput(Component):
    template_name = "inputs/text.html"

    def get_context_data(self, name="", placeholder="", value="", bonus_classes=""):
        return {
            "name": name,
            "placeholder": placeholder,
            "value": value,
            "bonus_classes": bonus_classes,
        }
