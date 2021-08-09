from django import template

from members.models import Member
from works.views import ItemRow, BookResult

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def get_user_books(member: Member, perms, handed_in=False):
    result = []
    for lending in member.lending_set.filter(handed_in=handed_in).prefetch_related("item__publication"):
        it = ItemRow(lending.item, extra_info=str(lending.end_date))
        if handed_in:
            result.append(BookResult(lending.item.publication, items=[it], item_options=[]))
        else:
            result.append(BookResult(lending.item.publication, items=[it], item_options=["extend", "return"]))
    return {"member": member, "perms": perms, "contents": result}


@register.inclusion_tag('publication_table/publication_table.html')
def get_user_reserved_books(member: Member, perms):
    result = []
    for lending in member.reservation_set.all().prefetch_related("item__publication"):
        it = ItemRow(lending.item)
        result.append(BookResult(lending.item.publication, items=[it], item_options=["lendFromRes", 'cancelRes']))
    return {"member": member, "perms": perms, "contents": result, 'reserve': True}
