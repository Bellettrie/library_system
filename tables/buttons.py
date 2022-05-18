import datetime

from django.contrib.auth.context_processors import PermWrapper
from django.template.loader import render_to_string

from lendings.procedures.extend import can_extend
from lendings.procedures.new_lending import can_lend
from members.models import Member
from tables.rows import ReservationRow, LendingRow, Row


class Button:
    def is_hidden(self, row, perms):
        return False

    def is_enabled(self, row, perms):
        return False, "-"

    def enabled_render(self, row, perms=None):
        return "enabled"

    def disabled_render(self, row, perms=None, err=None):
        return "enabled"

    def render(self, row, perms):
        if self.is_hidden(row, perms):
            return ""
        is_e, dis = self.is_enabled(row, perms)
        if is_e:
            return self.enabled_render(row, perms)
        else:
            return self.disabled_render(row, perms, dis)


class LendingTableReturnButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

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

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return not row.is_item()
        return True

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/lend_item.html", {"item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/lend_item_disabled.html", {"err": err})


class FinalizeLendingButton(Button):

    def __init__(self, member: Member):
        self.member = member

    def is_enabled(self, row: Row, perms: PermWrapper):
        cl = can_lend(row.get_item(), self.member, datetime.datetime.now().date())
        return not cl, cl

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return False
        return not row.is_item()

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/finalize_lending_button.html", {"item": row.get_item(), "member": self.member})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/finalize_lending_disabled_button.html",
                                {"err": err})


class FinalizeReservationButton(Button):
    def __init__(self, member: Member, for_self=False):
        self.member = member
        self.for_self = for_self

    def is_enabled(self, row, perms: PermWrapper):
        return (not row.get_item().is_available_for_lending()) and row.get_item().in_available_state(), "-"

    def is_hidden(self, row, perms: PermWrapper):
        if not self.member:
            return True
        if perms["reservations"]["reservations.add_reservation"]:
            return not row.is_item()
        return True

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/reserve_item_button.html",
                                {"item": row.get_item(), "member": self.member, "perms": perms,
                                 "for_self": self.for_self})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/reserve_item_disabled_button.html",
                                {"item": row.get_item(), "member": self.member, "perms": perms,
                                 "for_self": self.for_self})


class ReturnBookButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out(), "-"

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return not row.is_item()
        return True

    def enabled_render(self, row, perms=None):
        return render_to_string("buttons/return_item_button.html", {"lending": row.get_item().current_lending()})

    def disabled_render(self, row, perms=None, err=None):
        return render_to_string("buttons/return_item_disabled_button.html", {})


class IsLentOutStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out(), "-"

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return True
        return not row.is_item()

    def enabled_render(self, row, perms=None):
        return "<i>Lent Out</i>"

    def disabled_render(self, row, perms=None, err=None):
        return ""


class NotInAvailableStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def is_hidden(self, row, perms: PermWrapper):
        if str(row.get_item().get_state()) != "AVAILABLE":
            return not row.is_item()
        return True

    def enabled_render(self, row, perms=None):
        return "[{}]".format(row.get_item().get_state())


class ReservationCancelButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return True, "-"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_cancel_button.html", {"reservation": row.reservation})


class ReservationLendButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms: PermWrapper):
        return not row.get_item().is_lent_out(), "Item is lent out"

    def enabled_render(self, row: ReservationRow, perms=None):
        return render_to_string("buttons/reservation_finalize_button.html", {"reservation": row.reservation})

    def disabled_render(self, row: ReservationRow, perms=None, err=None):
        return render_to_string("buttons/reservation_finalize_disabled_button.html", {"err": err})


class ExtendButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row: LendingRow, perms: PermWrapper):
        e = can_extend(row.lending, datetime.datetime.now().date())
        return not e, e

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/extend_button.html", {"item": row.get_item()})

    def disabled_render(self, row: LendingRow, perms=None, err=None):
        return render_to_string("buttons/extend_button_disabled.html", {"err": err})


class StatusButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/status_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return str(row.get_item().get_state().get_type_display())


class StatusChangeButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/status_change_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return ""


class ItemEditButton(Button):
    def is_hidden(self, row, perms):
        return not row.is_item()

    def is_enabled(self, row, perms):
        return perms["works"]["change_publication"], "-"

    def enabled_render(self, row: LendingRow, perms=None):
        return render_to_string("buttons/item_edit_button.html",
                                {"status": row.get_item().get_state(), "item": row.get_item()})

    def disabled_render(self, row, perms=None, err=None):
        return ""


class NoItemsButton(Button):
    def is_hidden(self, row, perms):
        return row.is_item()

    def is_enabled(self, row, perms):
        return True, ""

    def enabled_render(self, row: LendingRow, perms=None):
        return "<i>Not in collection</i>"
