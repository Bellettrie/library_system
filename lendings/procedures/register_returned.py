from datetime import datetime

from lendings.models import Lending
from members.models import Member
from reservations.procedures.mail_when_returned import mail_when_returned


def register_returned(lending: Lending, member: Member, now=None):
    if now is None:
        now = datetime.date(datetime.now())
    lending.handed_in = True
    lending.handed_in_on = now
    lending.handed_in_by = member
    lending.save()
    lending.item.is_seen("Book was returned")


# Same as above, but also mail whoever reserved it, if one exists
def register_returned_with_mail(lending: Lending, member: Member, now=None):
    register_returned(lending, member, now)
    mail_when_returned(lending)
