from django import template

from members.models import Member
from works.views import ItemRow, BookResult

register = template.Library()


@register.inclusion_tag('publication_table/publication_table.html')
def get_user_books(member: Member, perms):
    result = []
    for lending in member.lending_set.filter(handed_in=False):
        it = ItemRow(lending.item, extra_info=str(lending.end_date))
        result.append(BookResult(lending.item.publication, [it], item_options=["extend", "return"]))
    return {"member": member, "perms": perms, "contents": result}
