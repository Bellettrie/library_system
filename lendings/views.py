from datetime import datetime, timedelta

from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from lendings.models import Lending, Reservation
from lendings.path_names import LENDING_FINALIZE, RESERVE_FINALIZE
from members.models import Member
from works.models import Item
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
                  {'members': members, 'item': get_object_or_404(Item, pk=work_id),
                   "LENDING_FINALIZE": LENDING_FINALIZE})


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
                  {'items': items, 'member': get_object_or_404(Member, pk=member_id),
                   "LENDING_FINALIZE": LENDING_FINALIZE})


lending_failed_reasons = {
    0: "Member has too many books",
    1: "Member is not presently a member",
    2: "Item is lent out",
    3: "Member has late items",
    4: "Item is reserved"
}


@login_required()
def lending_failed(request, member_id, work_id, reason_id):
    item = get_object_or_404(Item, pk=work_id)
    member = get_object_or_404(Member, pk=member_id)
    organising_member = request.user.member
    return render(request, 'lending_cannot_lend.html', {'item': item,
                                                        'member': member, 'organising_member': organising_member,
                                                        'reason': lending_failed_reasons[reason_id]})


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize(request, work_id, member_id):
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if item.is_available_for_lending():
        if request.method == 'POST':
            if not member.can_lend_item_type(item.location.category.item_type):
                return redirect('/lend/failed_lending/{}/{}/0'.format(work_id, member_id))
            if not member.is_currently_member():
                return redirect('/lend/failed_lending/{}/{}/1'.format(work_id, member_id))
            if member.has_late_items():
                return redirect('/lend/failed_lending/{}/{}/3'.format(work_id, member_id))
            if item.is_reserved() and not item.is_reserved_for(member):
                return redirect('/lend/failed_lending/{}/{}/4'.format(work_id, member_id))
            lending = Lending.create_lending(item, member, request.user.member)
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        return render(request, 'lending_finalize.html',
                      {'member': member, 'item': item, "date": Lending.calc_end_date(member, item)})
    return redirect('/lend/failed_lending/{}/{}/2'.format(work_id, member_id))


@transaction.atomic
def extend(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()
    if not request.user.has_perm('lendings.extend'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member == request.user.member):
            raise PermissionDenied
    late_days = datetime.now().date() - lending.end_date
    if lending.is_extendable(request.user.has_perm('lendings.extend_with_fine')):
        if request.method == 'POST':
            lending.extend(request.user.member)
            return render(request, 'lending_extended.html',
                          {'member': lending.member,
                           'item': item,
                           "date": lending.end_date
                           })
        return render(request, 'lending_extend.html',
                      {'member': lending.member,
                       'item': item,
                       'end_date': lending.end_date,
                       'is_changed': lending.end_date < Lending.calc_end_date(lending.member, item),
                       "date": Lending.calc_end_date(lending.member, item),
                       'late': lending.end_date < datetime.now().date(),
                       'days_late': late_days.days,
                       'fine': lending.calculate_fine()
                       })
    print("Cannot extend")
    return redirect('/members/' + str(lending.member.pk))


@transaction.atomic
@permission_required('lendings.return')
def return_book(request, work_id):
    item = get_object_or_404(Item, pk=work_id)
    lending = item.current_lending()
    late_days = datetime.now().date() - lending.end_date
    if request.method == 'POST':
        lending.register_returned(request.user.member)
        return redirect('/members/' + str(lending.member.pk))  # TODO intermediate page
    return render(request, 'return_book.html', {'item': item, 'lending': lending,
                                                'late': lending.end_date < datetime.now().date(),
                                                'days_late': late_days.days,
                                                'fine': lending.calculate_fine()})


@login_required()
def me(request):
    return render(request, 'lending_detail.html', {"member": request.user.member})


@permission_required('lendings.add_reservation')
def reserve_list(request):
    reservations = Reservation.objects.order_by('reserved_on')
    return render(request, 'reservation_list.html', {'reservations': reservations})


@permission_required('lendings.add_reservation')
def reserve_item(request, work_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    members = []
    if q is not None:
        members = Member.objects.filter(name__icontains=q)
    return render(request, 'reserve_based_on_work.html',
                  {'members': members, 'item': get_object_or_404(Item, pk=work_id),
                   "RESERVE_FINALIZE": RESERVE_FINALIZE})


@permission_required('lendings.add_reservation')
def reserve_member(request, member_id):
    q = None
    if 'q' in request.GET.keys():
        q = request.GET.get('q')
    items = []
    if q is not None:
        items = get_works(request)
        for row in items:
            row.set_item_options(["finalize"])

    return render(request, 'reserve_based_on_member.html',
                  {'items': items, 'member': get_object_or_404(Member, pk=member_id),
                   "RESERVE_FINALIZE": RESERVE_FINALIZE})


@transaction.atomic
def reserve_finalize(request, work_id, member_id):
    if not request.user.has_perm('lendings.add_reservation'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member
        if not (member and member.id == member_id):
            raise PermissionDenied
    member = get_object_or_404(Member, pk=member_id)
    item = get_object_or_404(Item, pk=work_id)
    if request.method == 'POST':
        if not member.can_lend_item_type(item.location.category.item_type):
            return redirect('/lend/failed_reservation/{}/{}/0'.format(work_id, member_id))
        if not member.is_currently_member():
            return redirect('/lend/failed_reservation/{}/{}/1'.format(work_id, member_id))
        if member.has_late_items():
            return redirect('/lend/failed_reservation/{}/{}/3'.format(work_id, member_id))
        if item.is_reserved():
            return redirect('/lend/failed_reservation/{}/{}/4'.format(work_id, member_id))
        Reservation.create_reservation(item, member, request.user.member)
        return render(request, 'reserve_finalized.html',
                      {'member': member, 'item': item})

    return render(request, 'reserve_finalize.html',
                  {'member': member, 'item': item, "date": Lending.calc_end_date(member, item)})


@login_required()
def reserve_failed(request, member_id, work_id, reason_id):
    item = get_object_or_404(Item, pk=work_id)
    member = get_object_or_404(Member, pk=member_id)
    organising_member = request.user.member
    return render(request, 'reservation_cannot_reserve.html', {'item': item,
                                                               'member': member, 'organising_member': organising_member,
                                                               'reason': lending_failed_reasons[reason_id]})


@transaction.atomic
@permission_required('lendings.add_lending')
def finalize_reservation_based(request, id):
    reservation = get_object_or_404(Reservation, pk=id)
    member = reservation.member
    item = reservation.item
    if item.is_available_for_lending():
        if request.method == 'POST':
            if not member.can_lend_item_type(item.location.category.item_type):
                return redirect('/lend/failed_lending/{}/{}/0'.format(item.id, member.id))
            if not member.is_currently_member():
                return redirect('/lend/failed_lending/{}/{}/1'.format(item.id, member.id))
            if member.has_late_items():
                return redirect('/lend/failed_lending/{}/{}/3'.format(item.id, member.id))
            reservation.delete()
            lending = Lending.create_lending(item, member, request.user.member)
            return render(request, 'lending_finalized.html',
                          {'member': member, 'item': item, "date": lending.end_date})
        return render(request, 'lending_finalize.html',
                      {'member': member, 'item': item, "date": Lending.calc_end_date(member, item)})
    return redirect('/lend/failed_lending/{}/{}/2'.format(item.id, member.id))


@login_required
def delete_reservation(request, id):
    reservation = get_object_or_404(Reservation, pk=id)
    if not request.user.has_perm('lendings.add_reservation'):
        if not hasattr(request.user, 'member'):
            raise PermissionDenied
        member = request.user.member

        if not (member and member.id == reservation.member_id):
            raise PermissionDenied
    if not request.GET.get('confirm'):
        return render(request, 'are-you-sure.html', {'what': "Delete reservation for book " + reservation.item.publication.get_title()})

    reservation.delete()

    return render(request, 'res_delete.html')
