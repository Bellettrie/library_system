from django_components import Component, register

from works.models import Item


@register("works.table.standard_card.Card")
class Card(Component):
    def get_context_data(self, item: Item, perms, work=None) -> dict:
        code = item.book_code
        authors = item.work.get_deduplicated_authors()

        authors = authors[:1]
        return {
            "item": item,
            "work": work or item.work,
            "authors": authors,
            "split_code": code.split("-"),
        }

    template_name = "works/table/standard_card/card.html"
