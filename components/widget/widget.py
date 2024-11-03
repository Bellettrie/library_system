from django.urls import reverse
from django_components import Component, register, types

@register("widget/widget_base")
class BaseWidget(Component):
    template_name = "widget/widget.html"

