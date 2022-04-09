from lendings.models import Lending
from mail.models import mail_member
from reservations.models import Reservation


def mail_when_returned(lending: Lending):
    for res in Reservation.objects.filter(lending.item):
        mail_member('mails/reservation_mail_returned.tpl',
                    {'member': res.member, 'item': res.item}, res.member, True)
        return
