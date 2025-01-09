import datetime

from django.contrib.auth.context_processors import PermWrapper
from django.template.loader import render_to_string

from lendings.procedures.extend import can_extend
from lendings.procedures.new_lending import can_lend
from members.models import Member
from tables.rows import ReservationRow, LendingRow, Row
from utils.time import get_today


class Button:
    def is_visible(self, row, perms):
        return True

    def is_enabled(self, row, perms):
        return False, "-"

    def enabled_render(self, row, perms=None):
        return "enabled"

    def disabled_render(self, row, perms=None, err=None):
        return "enabled"

    def render(self, row, perms):
        if not self.is_visible(row, perms):
            return ""
        is_e, dis = self.is_enabled(row, perms)
        if is_e:
            return self.enabled_render(row, perms)
        else:
            return self.disabled_render(row, perms, dis)


class LendingTableXsReturnButton(Button):
    def is_visible(self, row, perms) -> bool:
        return row.is_item()

    def is_enabled(self, row, perms):
        return True, "-"

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/return_item_button_xs.html", {"lending": row.lending})


class LendingTableReturnButton(Button):
    def is_visible(self, row, perms) -> bool:
        return row.is_item()

    def is_enabled(self, row, perms):
        return True, "-"

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/return_item_button.html", {"lending": row.lending})


class LendBookButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        if row.get_item().is_lent_out():
            return False, "Item is lent out"
        if not row.get_item().in_available_state():
            return False, "Item is in an unavailable state"
        return True, None

    def is_visible(self, row, perms: PermWrapper):
        if "lendings.add_lending" in perms:
            return row.is_item() and not row.get_item().is_lent_out()
        return False

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/lend_item.html", {"item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/lend_item_disabled.html", {"err": err})


class FinalizeLendingButton(Button):

    def __init__(self, member: Member):
        self.member = member

    def is_enabled(self, row: Row, perms: PermWrapper):
        cl = can_lend(row.get_item(), self.member, get_today())
        return not cl, cl

    def is_visible(self, row, perms: PermWrapper):
        if "lendings.add_lending" in perms:
            return row.is_item()
        return False

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/finalize_lending_button.html", {"item": row.get_item(), "member": self.member})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/finalize_lending_disabled_button.html",
                                {"err": err})


class FinalizeReservationButton(Button):
    def __init__(self, member: Member):
        self.member = member

    def is_enabled(self, row, perms: PermWrapper):
        if row.get_item().is_reserved():
            return False, "Item is reserved"
        if not row.get_item().is_lent_out():
            return False, "Item is in the room"
        if not row.get_item().is_available_for_reservation():
            return False, "Item is in an unreservable state"
        return True, None

    def is_visible(self, row, perms: PermWrapper):
        if self.member:
            return row.is_item()
        return False

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/reserve_item_button.html",
                                {"item": row.get_item(), "member": self.member, "perms": perms})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/reserve_item_disabled_button.html",
                                {"item": row.get_item(), "member": self.member, "perms": perms,
                                 "err": err})


class ReturnBookButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out(), "-"

    def is_visible(self, row, perms: PermWrapper):
        if "lendings.add_lending" in perms:
            return row.is_item() and row.get_item().is_lent_out()
        return False

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/return_item_button_xs.html", {"lending": row.get_item().current_lending()})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/return_item_disabled_button.html", {})


# Show status of the book for people who are not allowed to lend out books
class IsLentOutStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out(), "-"

    def is_visible(self, row, perms: PermWrapper):
        if "lendings.add_lending" not in perms:
            return row.is_item()
        return False

    def enabled_render(self, row, perms=None):
        return "<i>Lent Out</i>"

    def disabled_render(self, row, perms=None, err=None):
        return ""


class NotInAvailableStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def is_visible(self, row, perms: PermWrapper):
        if str(row.get_item().get_state()) != "AVAILABLE":
            return row.is_item()
        return False

    def enabled_render(self, row, perms=None):
        return "[{}]".format(row.get_item().get_state())


class ReservationCancelButton(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_cancel_button.html", {"reservation": row.reservation})


class ReservationCancelButtonXs(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_cancel_button_xs.html", {"reservation": row.reservation})

class ReservationLendButton(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return not row.get_item().is_lent_out(), "Item is lent out"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_finalize_button.html", {"reservation": row.reservation})

    def disabled_render(self, row: ReservationRow, perms=None, err=None):
        return render_to_string("buttons/reservation_finalize_disabled_button.html", {"err": err})


class ReservationLendButtonXs(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return not row.get_item().is_lent_out(), "Item is lent out"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_finalize_button_xs.html", {"reservation": row.reservation})

    def disabled_render(self, row: ReservationRow, perms=None, err=None):
        return render_to_string("buttons/reservation_finalize_disabled_button_xs.html", {"err": err})


class ExtendButton(Button):
    def is_visible(self, row: LendingRow, perms):
        return row.is_item() and not row.lending.handed_in

    def is_enabled(self, row: LendingRow, perms: PermWrapper):
        e = can_extend(row.lending, get_today())
        return not e, e

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/extend_button.html", {"item": row.get_item()})

    def disabled_render(self, row: LendingRow, perms=None, err=None):
        return render_to_string("buttons/extend_button_disabled.html", {"err": err})


class LendingHistoryButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def is_visible(self, row, perms: PermWrapper):
        if "lendings.add_lending" in perms:
            return row.is_item()
        return False

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/lend_history_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})


class StatusButton(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/status_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return str(row.get_item().get_state().get_type_display())


class StatusChangeButton(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/status_change_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return ""


class ItemEditButton(Button):
    def is_visible(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/item_edit_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return ""


class NoItemsButton(Button):
    def is_visible(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms):
        return True, ""

    def enabled_render(self, row: LendingRow, perms=None):
        return "<i>Not in collection</i>"
