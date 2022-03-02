
from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models.lending import Lending
from lendings.path_names import LENDING_FINALIZE
from members.models import Member

from works.models import Item
from works.views import get_works


@permission_required('lendings.add_lending')
def item_based(request, work_id):
    from members.views import query_members
    from utils.get_query_words import get_query_words
    words = get_query_words(request.GET.get("q"))
    members = query_members(words)
    return render(request, 'lending_based_on_work.html',
                  {'members': members, 'item': get_object_or_404(Item, pk=work_id),
                   "LENDING_FINALIZE": LENDING_FINALIZE})