from _datetime import datetime, timedelta

from config.tests import LendingSettingsBase
from lendings.lendingException import LendingImpossibleException
from lendings.procedures.register_returned import register_returned
from lendings.procedures.extend import extend_lending, new_extension
from lendings.procedures.get_total_fine import get_total_fine_for_days, get_total_fine_for_lending
from lendings.procedures.new_lending import create_lending, new_lending
from members.exceptions import AnonymisationException
from members.models import MembershipPeriod, MemberBackground
from members.procedures.anonymise import anonymise_or_except, anonymise_member
from members.tests import MemberSetup
from reservations.procedures.new_reservation import new_reservation
from works.models import Location, Category
from works.tests import item_create


class LendingBase(LendingSettingsBase, MemberSetup):
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


class LendingFailureCases(LendingBase):
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

    def test_member_has_late_books(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        create_lending(self.item1, self.member, self.member2, datetime.date(datetime(2020, 1, 11)))
        self.attempt_to_fail_lending(
            "Member currently has items that are late. These need to be returned before it can be handed out.")

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
        MembershipPeriod.objects.create(member=self.member2, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        MembershipPeriod.objects.create(member=self.member3, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_lending(self.item, self.member3, self.member2, current_date=datetime.date(datetime(2020, 2, 12)))
        new_reservation(self.item, self.member2, self.member2, current_date=datetime.date(datetime(2020, 2, 12)))
        self.attempt_to_fail_lending("Item is reserved for another member")

    def test_membership_period_starts_again_after(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-02-15", end_date="2020-06-20",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.attempt_to_fail_lending("End date for this lending would be in the past, cannot lend.")

    def test__two_membership_periods_starts_again_after(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-02-01", end_date="2020-02-20",
                                        membership_type=self.membership_type, member_background=self.member_background)
        MembershipPeriod.objects.create(member=self.member, start_date="2020-02-15", end_date="2020-06-20",
                                        membership_type=self.membership_type,
                                        member_background=MemberBackground.objects.create(name="T", visual_name="2"))
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.assertEqual((lending.end_date - datetime.date(datetime(2020, 2, 12))).days, 21)


class LendingSuccess(LendingBase):
    def test_membership_period(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.assertEqual((lending.end_date - datetime.date(datetime(2020, 2, 12))).days, 21)

    def test_membership_period_too_short(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-02-20",
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.assertEqual((lending.end_date - datetime.date(datetime(2020, 2, 12))).days, 8)

    def test_honorary_member(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date=None,
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))
        self.assertEqual((lending.end_date - datetime.date(datetime(2020, 2, 12))).days, 21)


class LendingExtend(LendingBase):
    def setUp(self):
        super(LendingExtend, self).setUp()
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.lending = create_lending(self.item, self.member, self.member2, datetime.date(datetime(2020, 2, 12)))

    def test_extend(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        extend_lending(self.lending, datetime.date(datetime(2020, 2, 14)))
        self.assertEqual((self.lending.end_date - datetime.date(datetime(2020, 2, 14))).days, 21)

    def test_extend_too_many(self):
        new_extension(self.lending, datetime.date(datetime(2020, 2, 14)))
        new_extension(self.lending, datetime.date(datetime(2020, 2, 15)))

        err_str = ""
        try:
            new_extension(self.lending, datetime.date(datetime(2020, 2, 16)))
        except LendingImpossibleException as err:
            err_str = str(err)
        self.assertEqual(err_str, "Item at max number of extensions")

    def test_extend_late(self):
        err_str = ""
        try:
            new_extension(self.lending, self.lending.end_date + timedelta(days=1))
        except LendingImpossibleException as err:
            err_str = str(err)
        self.assertEqual(err_str, "This item is late, and needs to be handed in.")

    def test_extend_reserved(self):
        MembershipPeriod.objects.create(member=self.member2, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_reservation(self.item, self.member2, self.member2, current_date=datetime.date(datetime(2020, 2, 12)))
        err_str = ""
        try:
            new_extension(self.lending, datetime.date(datetime(2020, 2, 14)))
        except LendingImpossibleException as err:
            err_str = str(err)
        self.assertEqual(err_str, "Item is already reserved")


class CalculateFine(LendingBase):
    def test_fine_amount_zero(self):
        self.assertEqual(get_total_fine_for_days(0, self.a), 0)

    def test_fine_min_amount(self):
        self.assertEqual(get_total_fine_for_days(1, self.a), 50)
        self.assertEqual(get_total_fine_for_days(7, self.a), 50)

    def test_fine_bump(self):
        self.assertEqual(get_total_fine_for_days(8, self.a), 100)

    def test_fine_near_max(self):
        self.assertEqual(get_total_fine_for_days(63, self.a), 450)

    def test_fine_max_amount(self):
        self.assertEqual(get_total_fine_for_days(64, self.a), 500)

    def test_for_lending(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2023-01-01", end_date="2023-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item, self.member, self.member2, datetime.date(datetime(2023, 2, 12)))
        self.assertEqual(get_total_fine_for_lending(lending, lending.end_date + timedelta(days=1)), 50)


class AnonymisationFailureTest(LendingBase):
    def attempt_to_fail_anonymisation(self, str_value):
        err_str = ""
        try:
            anonymise_or_except(self.member, datetime.date(datetime(2020, 2, 12)))
        except AnonymisationException as err:
            err_str = str(err)
        self.assertEqual(err_str, str_value)

    def test_already_anonymised(self):
        anonymise_member(self.member, False)
        self.attempt_to_fail_anonymisation("Already anonymised")

    def test_is_blacklisted(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.member.is_blacklisted = True
        self.attempt_to_fail_anonymisation("Is blacklisted")

    def test_is_still_member(self):
        MembershipPeriod.objects.create(member=self.member, start_date="2020-01-01", end_date="2020-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.attempt_to_fail_anonymisation("Is currently a member")

    def test_is_active(self):
        self.attempt_to_fail_anonymisation("Member is still active")

    def test_has_logged_in_member(self):
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.user.last_login = datetime(2020, 1, 12)
        self.member.save()
        self.attempt_to_fail_anonymisation("Logged in recently;  will be anonymised in 369 days.")

    def test_was_recently_a_member(self):
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.save()
        MembershipPeriod.objects.create(member=self.member, start_date="2019-01-01", end_date="2019-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        self.attempt_to_fail_anonymisation("Was recently a member; can be anonymised in 549 days.")

    def test_still_has_book(self):
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.save()
        MembershipPeriod.objects.create(member=self.member, start_date="2017-01-01", end_date="2017-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_lending(self.item1, self.member, self.member2, datetime.date(datetime(2017, 2, 12)))
        self.attempt_to_fail_anonymisation("Still has a book lent.")

    def test_recently_returned_book(self):
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.save()
        MembershipPeriod.objects.create(member=self.member, start_date="2017-01-01", end_date="2017-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        lending = new_lending(self.item1, self.member, self.member2, datetime.date(datetime(2017, 2, 12)))
        register_returned(lending, self.member2, datetime.date(datetime(2020, 1, 12)))
        self.attempt_to_fail_anonymisation("Recently lent a book")

    def test_still_has_reservation(self):
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.save()
        # A second member lending the item first is needed here to allow the reservation to be made
        MembershipPeriod.objects.create(member=self.member, start_date="2017-01-01", end_date="2017-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        MembershipPeriod.objects.create(member=self.member3, start_date="2017-01-01", end_date="2017-06-06",
                                        membership_type=self.membership_type, member_background=self.member_background)
        new_lending(self.item, self.member3, self.member2, datetime.date(datetime(2017, 2, 12)))
        new_reservation(self.item, self.member, self.member2, current_date=datetime.date(datetime(2017, 2, 12)))
        self.attempt_to_fail_anonymisation("Still has a reservation")
