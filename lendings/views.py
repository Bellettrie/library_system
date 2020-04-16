from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from config.models import LendingSettings
from lendings.models import Lending
from lendings.path_names import LENDING_FINALIZE
from members.models import Member
from works.models import Work, Item
from works.views import get_works


@permission_required('lendings.add_lending')
def index(request):
    lendings = Lending.objects.filter(handed_in=False).order_by('end_date')
    return render(request, 'lending_list.html', {'lendings': lendings})


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


@permission_required('lendings.add_lending')
def member_based(request, member_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    items = []
    if q is not None:
        items = get_works(request)
        for row in items:
            row.set_item_options(["finalize"])

    return render(request, 'lending_based_on_member.html',
                  {'items': items, 'member': Member.objects.get(pk=member_id), "LENDING_FINALIZE": LENDING_FINALIZE})


lending_failed_reasons = {
    0: "Member has too many books",
    1: "Member is not presently a member",
    2: "Item is lent out",
    3: "Member has late items"
}


@login_required()
def lending_failed(request, member_id, work_id, reason_id):
    item = Item.objects.get(pk=work_id)
    member = Member.objects.get(pk=member_id)
    organising_member = request.user.member
    return render(request, 'lending_cannot_lend.html', {'item': item,
                                                        'member': member, 'organising_member': organising_member, 'reason': lending_failed_reasons[reason_id]})


@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id):
    member = Member.objects.get(pk=member_id)
    item = Item.objects.get(pk=work_id)
    if item.is_available():
        if request.method == 'POST':
            if not member.can_lend_item_type(item.location.category.item_type):
                return redirect('/lend/failed_lending/{}/{}/0'.format(work_id, member_id))
            if not member.is_currently_member():
                return redirect('/lend/failed_lending/{}/{}/1'.format(work_id, member_id))
            if member.has_late_items():
                return redirect('/lend/failed_lending/{}/{}/3'.format(work_id, member_id))
            if not item.is_available():
                return redirect('/lend/failed_lending/{}/{}/2'.format(work_id, member_id))
            lending = Lending.create_lending(item, member, request.user.member)
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        return render(request, 'lending_finalize.html',
                      {'member': member, 'item': item, "date": Lending.calc_end_date(member, item)})
    return redirect('/members/' + str(member_id))


@permission_required('lendings.extend')
def extend(request, work_id):
    item = Item.objects.get(pk=work_id)
    lending = item.current_lending()
    late_days = datetime.now().date() - lending.end_date
    if lending.is_extendable(request.user.has_perm('lendings.extend_with_fine')):
        if request.method == 'POST':
            lending.extend(request.user.member)
            return render(request, 'lending_finalized.html',
                          {'member': lending.member,
                           'item': item,
                           "date": lending.end_date
                           })
        return render(request, 'lending_extend.html',
                      {'member': lending.member,
                       'item': item,
                       "date": Lending.calc_end_date(lending.member, item),
                       'late': lending.end_date < datetime.now().date(),
                       'days_late': late_days.days,
                       'fine': lending.calculate_fine()
                       })
    return redirect('/members/' + str(lending.member.pk))


@permission_required('lendings.return')
def return_book(request, work_id):
    item = Item.objects.get(pk=work_id)
    lending = item.current_lending().first()
    late_days = datetime.now().date() - lending.end_date
    if request.method == 'POST':
        lending.register_returned(request.user.member)
        return redirect('/members/' + str(lending.member.pk))  # TODO intermediate page
    return render(request, 'return_book.html', {'item': item, 'lending': lending,
                                                'late': lending.end_date < datetime.now().date(),
                                                'days_late': late_days.days,
                                                'fine': lending.calculate_fine()})


@login_required
def me(request):
    lendings = Lending.objects.filter(member=request.user.member)
    return render(request, 'lending_detail.html', {'lendings': lendings})
