from django_components import Component, register


@register("members.users.no_user")
class NoUser(Component):
    def get_context_data(self, member=""):
        return {
            "member": member,
        }

    template_name = "members/users/no_user.html"


@register("members.users.user")
class User(Component):
    def get_context_data(self, member=""):
        return {
            "member": member,
        }

    template_name = "members/users/existing_user.html"
