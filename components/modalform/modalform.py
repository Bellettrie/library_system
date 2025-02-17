from django_components import Component, register


@register("modalform.ModalForm")
class ModalForm(Component):
    template_name = "modalform/modalform.html"

    def get_context_data(self, path="#", title="", form_action="submit"):
        return {
            "form_path": path,
            "form_title": title,
            "form_action": form_action,
        }
