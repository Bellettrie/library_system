from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from config.models import LendingSettings
from lendings.models import Lending
from lendings.permissions import LENDING_FINALIZE
from members.models import Member
from works.models import Work, Item


@permission_required('lendings.add_lending')
def index(request):
    lendings = Lending.objects.filter(handed_in=False).order_by('end_date')
    return render(request, 'lending_base.html', {'lendings': lendings})


@permission_required('lendings.add_lending')
def work_based(request, work_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    members = []
    if q is not None:
        members = Member.objects.filter(name__icontains=q)
    return render(request, 'lending_based_on_work.html',
                  {'members': members, 'item': Item.objects.get(pk=work_id), "LENDING_FINALIZE": LENDING_FINALIZE})


def calc_end_date(member, item):
    now = datetime.now()
    term = LendingSettings.get_term(item, member)
    return now + timedelta(days=term)


@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id):
    member = Member.objects.get(pk=member_id)
    item = Item.objects.get(pk=work_id)
    if request.method == 'POST':
        post_values = request.POST
        newlending = Lending()
        newlending.end_date = calc_end_date(member, item)
        newlending.member = member
        newlending.item = item
        newlending.lended_on = datetime.now()
        newlending.last_extended = datetime.now()
        newlending.handed_in = False
        newlending.save()
        return render(request, 'finalized_lending.html')
    return render(request, 'finalize_lending.html',
                  {'member': member, 'item': item, "date": calc_end_date(member, item)})


@login_required
def me(request):
    lendings = Lending.objects.filter(member=request.user.member)
    return render(request, 'view-lending.html', {'lendings': lendings})
