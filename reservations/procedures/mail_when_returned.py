from datetime import timedelta

from lendings.models import Lending
from mail.models import mail_member
from reservations.models import Reservation
from utils.time import get_now

from django.conf import settings


def mail_when_returned(lending: Lending, now=None):
    if now is None:
        now = get_now()
    for res in Reservation.objects.filter(item=lending.item):
        mail_member('mails/reservation_mail_returned.tpl',
                    {'member': res.member, 'item': res.item}, res.member, True)
        res.reservation_end_date = now + timedelta(days=settings.RESERVATION_TIMEOUT_DAYS)
        res.save()
