from datetime import datetime

from config.models import LendingSettings
from lendings.lendingException import LendingImpossibleException
from lendings.models import Lending
from lendings.procedures.get_end_date import get_end_date
from lendings.procedures.get_fine_days import get_fine_days_for, get_fine_days
from members.models import Member
from works.models import Item


def create_lending(item: Item, member: Member, user_member: Member, current_date: datetime.date):
    if member.is_anonymous_user:
        raise LendingImpossibleException("Member {} is an anonymous user".format(member))
    from works.models import Item

    new_lending = Lending()

    from lendings.procedures.get_end_date import get_end_date
    new_lending.end_date = get_end_date(item, member, current_date)
    new_lending.member = member
    new_lending.item = item
    new_lending.lended_on = datetime.now()
    new_lending.last_extended = datetime.now()
    new_lending.handed_in = False
    new_lending.lended_by = user_member
    new_lending.save()
    item.is_seen("Book was lent out.")
    return new_lending


def lending_checks(item: Item, member: Member, current_date: datetime.date):
    if not member.can_lend_item(item):
        raise LendingImpossibleException("Member currently has lent too many items in category {}".format(item.location.category.item_type))
    if member.has_late_items():
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
    lending_checks(item, member, current_date)
    return create_lending(item, member, user_member, current_date)
