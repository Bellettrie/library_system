from _datetime import datetime

from config.models import LendingSettings
from lendings.lendingException import LendingImpossibleException
from lendings.models import Lending
from lendings.procedures.get_end_date import get_end_date_for_lending
from lendings.procedures.member_has_late_items import member_has_late_items


def extend_lending(lending: Lending, now: datetime.date):
    """Extend existing lending. Throws exception if book cannot be extended.
    :param lending: the lending to be extended
    :param now: what is the date on which the lending is extended?
    :return: None
    """
    lending.end_date = get_end_date_for_lending(lending, now)
    lending.last_extended = now
    lending.times_extended = lending.times_extended + 1
    lending.save()
    return lending


def extend_checks(lending: Lending, now: datetime.date):
    """
    Check whether an item can be lent by a member.
    :param lending: the lending to extend
    :param now: The date at which the item is lent
    :return: None
    :except LendingImpossibleException: If the lending-checks fail.
    """
    if member_has_late_items(lending.member, now):
        raise LendingImpossibleException(
            "Member currently has items that are late. These need to be returned before it can be handed in.")
    if lending.member.is_blacklisted:
        raise LendingImpossibleException("Member currently blacklisted, cannot lend")
    if lending.item.is_reserved():
        if not lending.item.is_reserved_for(lending.member):
            raise LendingImpossibleException("Item is reserved for another member")
    if not lending.item.in_available_state():
        raise LendingImpossibleException(
            "Item is not currently available for lending, the item is {}.".format(lending.item.get_state()))
    if lending.times_extended >= LendingSettings.get_for(lending.item, lending.member).extend_count:
        raise LendingImpossibleException("Item at max number of extensions")


def new_extension(lending: Lending, current_date: datetime.date):
    """
    Execute checks. If the checks pass, extend lending.
    :param lending: The lending to be extended
    :param current_date: The date at which the item is lent
    :return: A lending object, already persisted
    :except LendingImpossibleException: If the extension-checks fail.
    """
    extend_checks(lending, current_date)
    return extend_lending(lending, current_date)
