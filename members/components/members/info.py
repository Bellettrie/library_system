from django_components import Component, register


@register("members.basic_info")
class BasicInfo(Component):
    def get_context_data(self, members=""):
        return {
            "members": members,
        }

    template_name = "members/basic_info.html"


@register("members.detailed_info")
class DetailedInfo(Component):
    def get_context_data(self, members=""):
        return {
            "members": members,
        }

    template_name = "members/detailed_info.html"
