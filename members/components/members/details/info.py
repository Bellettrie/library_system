from django_components import Component, register

from members.models import Member


@register("members.basic_info")
class BasicInfo(Component):
    def get_context_data(self, member: Member):
        return {
            "member": member,
        }

    template_name = "members/details/info_basic.html"


@register("members.detailed_info")
class DetailedInfo(Component):
    def get_context_data(self, member: Member):
        return {
            "member": member,
        }

    template_name = "members/details/info_detailed.html"

@register("members.info.footer")
class InfoFooter(Component):
    def get_context_data(self, member: Member, is_on_details_view=False):
        return {
            "member": member,
            "is_on_details_view":is_on_details_view,
        }
    template_name = "members/details/info_footer.html"