from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from works.models import Item
from works.models.row_data import RowData


@permission_required('lendings.add_lending')
def item_based(request, item_id):
    from members.views.member_list import query_members
    from utils.get_query_words import get_query_words
    words = get_query_words(request.GET.get("q"))
    members = query_members(words)
    item = get_object_or_404(Item, pk=item_id)
    rowdata = RowData(item=item, work=item.publication)
    return render(request, 'lendings/based_on_work.html',
                  {'members': members, 'item': item, 'rowdata': rowdata})
