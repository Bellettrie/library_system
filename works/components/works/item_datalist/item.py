from django_components import Component, register

from works.models import Item


@register("works.item_datalist.Item")
class Item(Component):

    def get_context_data(self, item: Item, perms):
        return {
            "item": item,
            "perms": perms
        }

    template_name = "works/item_datalist/item.html"
