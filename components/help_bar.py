from django_components import Component, register

@register("help_bar")
class HelpBar(Component):
    template_name = "help_bar.html"
