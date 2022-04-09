from datetime import datetime

from fines.procedures.register_fine_for_returned import register_fine_for_returned
from lendings.models import Lending
from members.models import Member
from reservations.procedures.mail_when_returned import mail_when_returned


def register_returned(lending: Lending, member: Member, paid: bool, now=None):
    """
    Register that an item has been returned
    :param lending: the lending to be returned
    :param member: the member that registers the return
    :param paid: has the member paid for the fine, if it's there?
    :param now: the date at which the lending is returned
    :return: None
    """
    if now is None:
        now = datetime.date(datetime.now())
    lending.handed_in = True
    lending.handed_in_on = now
    lending.handed_in_by = member
    lending.save()
    lending.item.is_seen("Book was returned")


def register_returned_with_mail_and_fine_registration(lending: Lending, member: Member, paid: bool, now=None):
    """
    Register that an item has been returned, then send an e-mail to whoever has reserved it, if applicable.
    Also, register the fine.
    :param lending: the lending to be returned
    :param member: the member that registers the return
    :param paid: has the member paid for the fine, if it's there?
    :param now: the date at which the lending is returned
    :return: None
    """
    register_returned(lending, member, paid, now)
    register_fine_for_returned(lending, now, paid)
    mail_when_returned(lending)


