from datetime import datetime

from django.db import transaction

from lendings.lendingException import LendingImpossibleException
from lendings.models import Lending
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.member_has_late_items import member_has_late_items
from members.models import Member
from members.procedures.can_lend_more_of_item import can_lend_more_of_item
from reservations.models import Reservation
from works.models import Item


@transaction.atomic
def create_lending(item: Item, member: Member, user_member: Member, current_date: datetime.date):
    """
    Create a new lending.
    :param item: The item to be lent
    :param member: The member getting to lend the item
    :param user_member: The member registering the item being lent
    :param current_date: The date at which the item is lent
    :return: Lending object, already persisted
    :except LendingImpossibleException: If the member is anonymous
    """
    if member.is_anonymous_user:
        raise LendingImpossibleException("Member {} is an anonymous user".format(member))

    new_lending = Lending()
    from lendings.procedures.get_end_date import get_end_date
    new_lending.end_date = get_end_date(item, member, current_date)
    new_lending.member = member
    new_lending.item = item
    new_lending.lended_on = current_date
    new_lending.last_extended = current_date
    new_lending.handed_in = False
    new_lending.lended_by = user_member
    new_lending.save()
    reservations = Reservation.objects.filter(item=item)
    if len(reservations) > 0:
        reservation = reservations.first()
        reservation.delete()
    item.is_seen("Book was lent out.")
    return new_lending


def item_lending_checks(item: Item, current_date: datetime.date):
    if item.is_lent_out():
        raise LendingImpossibleException("Item is lent out")
    if not item.in_available_state():
        raise LendingImpossibleException(
            "Item is not currently available for lending, the item is {}.".format(item.get_state()))


def lending_checks(item: Item, member: Member, current_date: datetime.date, from_reservation=False):
    """
    Check whether an item can be lent by a member.
    :param item: The item to be lent
    :param member: The member getting to lend the item
    :param current_date: The date at which the item is lent
    :return: None
    :except LendingImpossibleException: If the lending-checks fail.
    """

    if not can_lend_more_of_item(member, item, from_reservation):
        raise LendingImpossibleException(
            "Member currently has lent too many items in category {}".format(item.location.category.item_type))
    if member_has_late_items(member, current_date):
        raise LendingImpossibleException(
            "Member currently has items that are late. These need to be returned before it can be handed out.")
    if member.is_blacklisted:
        raise LendingImpossibleException("Member currently blacklisted, cannot lend")

    item_lending_checks(item, current_date)
    if item.is_reserved():
        if not item.is_reserved_for(member):
            raise LendingImpossibleException("Item is reserved for another member")

    end_date = get_end_date(item, member, current_date)
    if end_date < current_date:
        raise LendingImpossibleException("End date for this lending would be in the past, cannot lend.")


def can_lend(item: Item, member: Member, current_date: datetime.date, from_reservation=False):
    try:
        lending_checks(item, member, current_date, from_reservation)
    except LendingImpossibleException as error:
        return error.__str__()


def item_can_be_lended(item: Item, current_date: datetime.date):
    try:
        item_lending_checks(item, current_date)
    except LendingImpossibleException as error:
        return error.__str__()


def new_lending(item: Item, member: Member, user_member: Member, current_date: datetime.date, from_reservation=False):
    """
    Execute checks. If the checks pass, create a new lending.
    :param item: The item to be lent
    :param member: The member getting to lend the item
    :param user_member: The member registering the item being lent
    :param current_date: The date at which the item is lent
    :return: A lending object, already persisted
    :except LendingImpossibleException: If the lending-checks fail.
    """
    lending_checks(item, member, current_date, from_reservation)
    return create_lending(item, member, user_member, current_date)
