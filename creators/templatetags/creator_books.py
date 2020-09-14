from django import template

from creators.models import Creator
from works.models import Publication, Item
from works.views import ItemRow, BookResult

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def get_creator_books(creator: Creator, perms):
    result = []
    for work in Publication.objects.filter(creatortowork__creator=creator):
        it = []
        for item in Item.objects.filter(publication=work):
            it.append(ItemRow(item))

        result.append(BookResult(work, it, item_options=[]))
    return {"perms": perms, "contents": result}
