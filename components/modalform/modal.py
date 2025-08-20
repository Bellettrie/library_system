from django_components import Component, register

@register("modalform.Modal")
class ModalForm(Component):
    template_name = "modalform/modal.html"

    def get_context_data(self, title ):
        print(title)
        return {
            "title": title,
        }
