from datetime import datetime, timedelta

from django.shortcuts import render

# Create your views here.
from lendings.models import Lending
from lendings.permissions import LENDING_FINALIZE
from members.models import Member
from works.models import Work, Item

def index(request):
    lendings = Lending.objects.filter(handed_in=False).order_by('end_date')
    return render(request, 'lending_base.html', {'lendings': lendings})

def work_based(request, work_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    members = []
    if q is not None:
        members = Member.objects.filter(name__icontains=q)
    return render(request, 'lending_based_on_work.html', {'members': members, 'item': Item.objects.get(pk=work_id), "LENDING_FINALIZE": LENDING_FINALIZE})


def calc_end_date(member, item):
    now = datetime.now()
    return now + timedelta(days=21)


def finalize(request, work_id, member_id):
    member = Member.objects.get(pk=member_id)
    item = Item.objects.get(pk=work_id)
    return render(request, 'finalize_lending.html',
                  {'member': member, 'item': item, "date": calc_end_date(member, item)})


def me(request):
    lendings = Lending.objects.filter(member=request.user.member)
    return render(request, 'view-lending.html', {'lendings': lendings})
