from django_components import Component, register

from lendings.models import Lending


@register("lendings.card.Card")
class Card(Component):
    def get_context_data(self, lending: Lending, perms, show_member: bool = True):
        code = lending.item.book_code

        return {
            "lendings": lending,
            "split_code": code.split("-"),
            "show_member": show_member,
        }

    template_name = "lendings/card/card.html"
