# Buttons are a part of a button column.
# A button conditionally renders.
from django.contrib.auth.context_processors import PermWrapper
from django.template.loader import render_to_string

from members.models import Member


class Button:
    def is_hidden(self, row, perms):
        return False

    def is_enabled(self, row, perms):
        return False

    def enabled_render(self, row):
        return "enabled"

    def disabled_render(self, row):
        return "enabled"

    def render(self, row, perms):
        if self.is_hidden(row, perms):
            return ""
        if self.is_enabled(row, perms):
            return self.enabled_render(row)
        else:
            return self.disabled_render(row)


class LendingTableReturnButton(Button):
    def is_enabled(self, row, perms):
        return True

    def enabled_render(self, row):
        return render_to_string("buttons/return_item_button.html", {"lending": row.lending})


class LendBookButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_available_for_lending()

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"] and row.get_item().in_available_state():
            return False
        return True

    def enabled_render(self, row):
        return render_to_string("buttons/lend_item.html", {"item": row.get_item()})

    def disabled_render(self, row):
        return render_to_string("buttons/lend_item_disabled.html", {"item": row.get_item()})


class FinalizeLendingButton(Button):
    def __init__(self, member: Member):
        self.member = member

    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_available_for_lending() and True

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"] and row.get_item().in_available_state():
            return False
        return True

    def enabled_render(self, row):
        return render_to_string("buttons/finalize_lending_button.html", {"item": row.get_item(), "member": self.member})

    def disabled_render(self, row):
        return ""


class ReturnBookButton(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out()

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return False
        return True

    def enabled_render(self, row):
        return render_to_string("buttons/return_item_button.html", {"lending": row.get_item().current_lending()})

    def disabled_render(self, row):
        return render_to_string("buttons/return_item_disabled_button.html", {})


class IsLentOutStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return row.get_item().is_lent_out()

    def is_hidden(self, row, perms: PermWrapper):
        if perms["lendings"]["lendings.add_lending"]:
            return True
        return False

    def enabled_render(self, row):
        return "<i>Lent Out</i>"

    def disabled_render(self, row):
        return ""


class NotInAvailableStatus(Button):
    def is_enabled(self, row, perms: PermWrapper):
        return True

    def is_hidden(self, row, perms: PermWrapper):
        if str(row.get_item().get_state()) != "AVAILABLE":
            return False
        return True

    def enabled_render(self, row):
        return "[{}]".format(row.get_item().get_state())
