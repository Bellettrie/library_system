from datetime import datetime, timedelta

from django.db import transaction

from lendings.procedures.member_has_late_items import member_has_late_items
from members.models import Member
from members.procedures.can_lend_more_of_item import can_lend_more_of_item
from reservations.models import Reservation
from reservations.reservationException import ReservationImpossibleException
from works.models import Item
from utils.time import get_now


@transaction.atomic
def create_reservation(item, member: Member, edited_member: Member, current_date=None):
    if current_date is None:
        current_date = get_now()

    if member.is_anonymous_user:
        raise ValueError("Member is an anonymous user")

    new_reservation = Reservation()
    new_reservation.member = member
    new_reservation.item = item
    new_reservation.reserved_on = current_date
    new_reservation.reserved_by = edited_member

    new_reservation.save()
    return new_reservation


def assert_member_can_reserve(item, member, current_date):
    """
        Check whether an item can be lent by a member.
        :param item: The item to be reserved
        :param member: The member getting to reserve the item
        :param current_date: The date at which the item is reserved
        :return: None
        :except ReservationImpossibleException: If the reservation-checks fail.
    """
    if not can_lend_more_of_item(member, item, False):
        raise ReservationImpossibleException(
            "Member currently has lent too many items in category {}".format(item.location.category.item_type))
    if member_has_late_items(member, current_date):
        raise ReservationImpossibleException(
            "Member currently has items that are late. These need to be returned before it can be reserved.")
    if member.is_blacklisted:
        raise ReservationImpossibleException("Member currently blacklisted, cannot reserve")
    if not member.is_currently_member(current_date):
        raise ReservationImpossibleException("Member currently not a member, cannot reserve")
    if item.is_reserved():
        raise ReservationImpossibleException("Item is reserved for another member")
    if item.is_lent_out() and item.current_lending().member.id == member.id:
        raise ReservationImpossibleException("Cannot reserve books you have borrowed.")
    if not item.is_lent_out():
        raise ReservationImpossibleException("Cannot reserve books that are in the room.")
    if not item.in_available_state():
        raise ReservationImpossibleException(
            "Item is not currently available for reservation, the item is {}.".format(item.get_state()))


def can_reserve(item: Item, member: Member, current_date: datetime.date):
    try:
        assert_member_can_reserve(item, member, current_date)
    except ReservationImpossibleException as error:
        return error.__str__()


def new_reservation(item: Item, member: Member, user_member: Member, current_date: datetime.date):
    """
        Execute checks. If the checks pass, create a new reservation.
        :param item: The item to be reserved
        :param member: The member getting to reserve the item
        :param user_member: The member registering the item being reserved
        :param current_date: The date at which the item is reserved
        :except ReservationImpossibleException: If the reservation-checks fail.
    """
    assert_member_can_reserve(item, member, current_date)
    return create_reservation(item, member, user_member, current_date)
