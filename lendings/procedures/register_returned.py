from datetime import datetime

from lendings.models import Lending
from members.models import Member
from reservations.procedures.mail_when_returned import mail_when_returned
from utils.time import get_today


def register_returned(lending: Lending, member: Member, now=None):
    """
    Register that an item has been returned
    :param lending: the lending to be returned
    :param member: the member that registers the return
    :param now: the date at which the lending is returned
    :return: None
    """
    if now is None:
        now = get_today()
    lending.handed_in = True
    lending.handed_in_on = now
    lending.handed_in_by = member
    lending.save()
    lending.item.is_seen("Book was returned")


def register_returned_with_mail(lending: Lending, member: Member, now=None):
    """
    Register that an item has been returned, then send an e-mail to whoever has reserved it, if applicable.
 :param lending: the lending to be returned
    :param member: the member that registers the return
    :param now: the date at which the lending is returned
    :return: None
    """
    register_returned(lending, member, now)
    mail_when_returned(lending)
