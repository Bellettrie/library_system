from datetime import timedelta

from mail.models import mail_member
from reservations.models import Reservation
from utils.time import get_now


def clear_old_reservations(now=None):
    if now is None:
        now = get_now()
    for res in Reservation.objects.filter(reservation_end_date__lte=now):
        mail_member('mails/reservation_cancelled_late.tpl', {'member': res.member, 'item': res.item}, res.member, True)
        res.delete()


def clear_unavailable():
    for res in Reservation.objects.all():
        if not res.item.in_available_state():
            mail_member('mails/reservation_cancelled_unavailable.tpl', {'member': res.member, 'item': res.item},
                        res.member, True)
            res.delete()


def set_end_date_if_no_lent_out(now=None):
    for res in Reservation.objects.filter(reservation_end_date__isnull=True):
        print(res)
        if not res.item.is_lent_out():
            if now is None:
                now = get_now()
            res.reservation_end_date = now + timedelta(days=14)
            res.save()

def clear_not_member():
    for res in Reservation.objects.all():
        if not res.member.is_currently_member():
            mail_member('mails/reservation_cancelled_not_member.tpl', {'member': res.member, 'item': res.item},
                        res.member, True)
            res.delete()
