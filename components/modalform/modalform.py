from django_components import Component, register


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
