from datetime import datetime

from lendings.models import Lending
from members.models import Member


def register_returned(lending: Lending, member: Member, now=None):
    if now is None:
        now = datetime.date(datetime.now())
    lending.handed_in = True
    lending.handed_in_on = now
    lending.handed_in_by = member
    lending.save()
    lending.item.is_seen("Book was returned")
