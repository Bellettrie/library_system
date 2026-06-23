from django_components import Component, register


@register("lendings.buttons.Return")
class Return(Component):
    template_name = "lendings/buttons/return.html"

    def get_context_data(self, lending, user_member, user_permissions, bonus_classes=""):
        is_visible = not lending.handed_in
        if not user_permissions["lendings"]["change_lending"]:
            is_visible = False

        return {
            "is_visible": is_visible,
            "lending": lending,
            "bonus_classes": bonus_classes,
        }
