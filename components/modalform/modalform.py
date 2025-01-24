from django_components import Component, register


@register("modalform.ModalForm")
class ModalForm(Component):
    template_name = "modalform/modalform.html"

    def get_context_data(self, path="#", title= "", button_name="Submit", button_type="primary", btn_action="submit"):
        return {
            "form_path": path,
            "form_title": title,
            "form_button_name": button_name,
            "form_button_type": button_type,
            "btn_action": btn_action,
        }
