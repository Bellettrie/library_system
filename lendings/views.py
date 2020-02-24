from django.shortcuts import render

# Create your views here.
from members.models import Member
from works.models import Work, Item


def work_based(request, work_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    members = []
    if q is not None:
        members = Member.objects.filter(name__icontains=q)
    return render(request, 'lending_based_on_work.html', {'members': members, 'item': Item.objects.get(pk=work_id)})


def finalize(request, work_id, member_id):
    member = Member.objects.get(pk=member_id)
    item = Item.objects.get(pk=work_id)
    return render(request, 'finalize_lending.html', {'member': member, 'item': item})
