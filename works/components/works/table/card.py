from django_components import Component, register

from works.models import Item


@register("works.table.Card")
class Card(Component):
    def get_context_data(self, item: Item, all_authors=False):
        code = item.book_code
        authors = item.work.get_deduplicated_authors()
        if not all_authors:
            authors = authors[:1]
        return {
            "item": item,
            "authors": authors,
            "split_code": code.split("-"),
        }

    template_name = "works/table/card.html"
