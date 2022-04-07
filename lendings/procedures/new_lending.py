from datetime import datetime

from lendings.lendingException import LendingImpossibleException
from lendings.models import Lending
from lendings.procedures.get_end_date import get_end_date
from members.models import Member
from works.models import Item


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
    item.is_seen("Book was lent out.")
    return new_lending


def lending_checks(item: Item, member: Member, current_date: datetime.date):
    """
    Check whether an item can be lent by a member.
    :param item: The item to be lent
    :param member: The member getting to lend the item
    :param current_date: The date at which the item is lent
    :return: None
    :except LendingImpossibleException: If the lending-checks fail.
    """
    if not member.can_lend_item(item):
        raise LendingImpossibleException("Member currently has lent too many items in category {}".format(item.location.category.item_type))
    if member.has_late_items(current_date):
        raise LendingImpossibleException("Member currently has items that are late. These need to be returned before it can be handed in.")
    if member.is_blacklisted:
        raise LendingImpossibleException("Member currently blacklisted, cannot lend")
    if item.is_reserved():
        if not item.is_reserved_for(member):
            raise LendingImpossibleException("Item is reserved for another member")
    if item.is_lent_out():
        raise LendingImpossibleException("Item is lent out")
    if not item.in_available_state():
        raise LendingImpossibleException("Item is not currently available for lending, the item is {}.".format(item.get_state()))

    end_date = get_end_date(item, member, current_date)
    if end_date < current_date:
        raise LendingImpossibleException("End date for this lending would be in the past, cannot lend.")


def new_lending(item: Item, member: Member, user_member: Member, current_date: datetime.date):
    """
    Execute checks. If the checks pass, create a new lending.
    :param item: The item to be lent
    :param member: The member getting to lend the item
    :param user_member: The member registering the item being lent
    :param current_date: The date at which the item is lent
    :return: A lending object, already persisted
    :except LendingImpossibleException: If the lending-checks fail.
    """
    lending_checks(item, member, current_date)
    return create_lending(item, member, user_member, current_date)
