from django.test import TestCase

# Create your tests here.
from _datetime import datetime, timedelta
from config.tests import LendingSettingsBase
from lendings.procedures.new_lending import create_lending
from members.models import MembershipPeriod
from members.tests import MemberSetup
from reservations.procedures.new_reservation import new_reservation
from reservations.reservationException import ReservationImpossibleException
from works.models import Category, Location
from works.tests import item_create


class ReservationBase(LendingSettingsBase, MemberSetup):
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


class ReservationFailureCases(ReservationBase):
    def attempt_to_fail_reservation(self, str_value):
        err_str = ""
        try:
            new_reservation(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        except ReservationImpossibleException as err:
            err_str = str(err)
        self.assertEqual(err_str, str_value)

    def test_no_membership_period(self):
        self.attempt_to_fail_reservation("Member currently not a member, cannot reserve")

    def test_member_blacklisted(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.member.is_blacklisted = True
        self.attempt_to_fail_reservation("Member currently blacklisted, cannot reserve")

    def test_member_has_late_books(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        create_lending(self.item1, self.member, self.member2, datetime.date(datetime(2020, 1, 11)))
        self.attempt_to_fail_reservation(
            "Member currently has items that are late. These need to be returned before it can be reserved.")

    def test_too_many_lendings(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_reservation(self.item1, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_reservation(self.item2, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_reservation(self.item3, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_reservation(self.item4, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        new_reservation(self.item5, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.attempt_to_fail_reservation("Member currently has lent too many items in category Book")

    def test_already_reserved_someone_else(self):
        MembershipPeriod.objects.create(member=self.member2, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_reservation(self.item, self.member2, self.member2, current_date=datetime.date(datetime(2020, 2, 12)))
        self.attempt_to_fail_reservation("Item is reserved for another member")

    def test_membership_period_starts_again_after(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-02-15", end_date="2020-06-20",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.attempt_to_fail_reservation("Member currently not a member, cannot reserve")
