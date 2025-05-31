from django_components import Component, register


@register("datarow/datarow")
class BaseTile(Component):
    def get_context_data(self, name, root_class_tags=""):
        return {
            "name": name,
            "root_class_tags": root_class_tags,
        }

    template_name = "datarow/datarow.html"
