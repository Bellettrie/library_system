from django_components import Component, register

from works.models import Item


@register("works.item_datalist.Item")
class Item(Component):
    def get_context_data(self, item: Item, perms, work = None):
        return {
            "item": item,
            "work": work or item.work,
            "perms": perms
        }


template_name = "works/item_datalist/item.html"
