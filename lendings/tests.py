from _datetime import datetime
from django.test import TestCase

from config.tests import LendingSettingsBase
from lendings.lendingException import LendingImpossibleException
from lendings.models import Lending
from lendings.procedures.get_fine_days import get_fine_days
from lendings.procedures.new_lending import create_lending, new_lending
from members.models import MembershipPeriod
from members.tests import MemberSetup
from reservations.models import Reservation
from works.models import Location, Category
from works.tests import item_create


class LendingPreLendingTestCase(LendingSettingsBase, MemberSetup):
    item = None

    def setUp(self):
        self.lending_settings_create()
        self.member_setup()
        category = Category.objects.create(name="Boring Books", item_type=self.book)
        location = Location.objects.create(category=category, name="Hidden location", old_id=0)
        self.item = item_create("A collection of random words", location)
        self.item1 = item_create("1", location)
        self.item2 = item_create("2", location)
        self.item3 = item_create("3", location)
        self.item4 = item_create("4", location)
        self.item5 = item_create("5", location)

    def attempt_to_fail_lending(self, str_value):
        err_str = ""
        try:
            new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        except LendingImpossibleException as err:
            err_str = str(err)
        self.assertEqual(err_str, str_value)

    def test_no_membership_period(self):
        self.attempt_to_fail_lending("End date for this lending would be in the past, cannot lend.")

    def test_member_blacklisted(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.member.is_blacklisted = True
        self.attempt_to_fail_lending("Member currently blacklisted, cannot lend")

    def test_too_many_lendings(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_lending(self.item1, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_lending(self.item2, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_lending(self.item3, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_lending(self.item4, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_lending(self.item5, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.attempt_to_fail_lending("Member currently has lent too many items in category Book")

    def test_create_lending_already_lent_out(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        create_lending(self.item, self.member2, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.attempt_to_fail_lending("Item is lent out")

    def test_already_reserved_someone_else(self):
        Reservation.create_reservation(self.item, self.member2, self.member2, current_date=datetime(2020, 2, 12))
        self.attempt_to_fail_lending("Item is reserved for another member")

    def test_membership_period(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        print(lending.end_date)
