import datetime

from django.test import TestCase

# Create your tests here.
from config.models import Holiday, LendingSettings
from members.models import Member, Committee
from works.models import Publication, Item, Category, Location, ItemType
from works.tests import create_work


class LendingTermTestCase(TestCase):
    def setUp(self):
        # Holidays in different years
        Holiday.objects.create(name='Sleeping holiday',
                               starting_date=datetime.date(2022, 4, 4),
                               ending_date=datetime.date(2022, 5, 4),
                               skipped_for_fine=False)
        Holiday.objects.create(name='Very Short Holiday',
                               starting_date=datetime.date(2019, 1, 1),
                               ending_date=datetime.date(2019, 1, 1),
                               skipped_for_fine=False)
        p = create_work("The one book")
        item_type = ItemType.objects.create(name="Strip", old_id=0)
        category = Category.objects.create(name="TestCat", item_type=item_type)
        location = Location.objects.create(name="TestLoc", category=category, old_id=0)
        self.item = Item.objects.create(publication=p, old_id=0, hidden=False, location=location)
        self.member = Member.objects.create(end_date=datetime.date(2023, 4, 4))
        self.member2 = Member.objects.create(end_date=datetime.date(2021, 4, 4))
        committee = Committee.objects.create(active_member_committee=True, name="Active com")
        self.member3 = Member.objects.create(end_date=datetime.date(2021, 4, 4))
        self.member3.committees.add(committee)
        self.member3.save()
        self.lending_settings = LendingSettings.objects.create(item_type=item_type,
                                       term_for_inactive=7,
                                       term_for_active=14,
                                       hand_in_days=1,
                                       borrow_money_inactive=0,
                                       borrow_money_active=0,
                                       fine_amount=50,
                                       max_fine=500)

    def test_holiday_one_day(self):
        self.assertEqual(datetime.date(2019, 1, 2), LendingSettings.get_end_date(self.item, self.member, datetime.date(2018, 12, 31 - 6)))

    def test_holiday_longer_holiday(self):
        self.assertEqual(datetime.date(2022, 5, 5), LendingSettings.get_end_date(self.item, self.member, datetime.date(2022, 3, 30)))

    def test_membership_ends_early(self):
        self.assertEqual(datetime.date(2021, 4, 4), LendingSettings.get_end_date(self.item, self.member2, datetime.date(2022, 3, 30)))

    def test_no_holidays(self):
        self.assertEqual(datetime.date(2017, 1, 8), LendingSettings.get_end_date(self.item, self.member2, datetime.date(2017, 1, 1)))

    def test_end_date_not_in_noliday(self):
        self.assertEqual(datetime.date(2022, 5, 8), LendingSettings.get_end_date(self.item, self.member, datetime.date(2022, 5, 1)))

    def test_active_member(self):
        self.assertEqual(datetime.date(2019, 1, 2), LendingSettings.get_end_date(self.item, self.member3, datetime.date(2018, 12, 31 - 6 - 7)))

    def test_overlapping_holidays_abba(self):
        Holiday.objects.create(name='Sleeping holiday',
                               starting_date=datetime.date(2022, 4, 8),
                               ending_date=datetime.date(2022, 5, 2),
                               skipped_for_fine=False)
        self.assertEqual(datetime.date(2022, 5, 5), LendingSettings.get_end_date(self.item, self.member, datetime.date(2022, 3, 30)))

    def test_overlapping_holidays_abab(self):
        Holiday.objects.create(name='Sleeping holiday',
                               starting_date=datetime.date(2022, 4, 8),
                               ending_date=datetime.date(2022, 5, 8),
                               skipped_for_fine=False)
        self.assertEqual(datetime.date(2022, 5, 9), LendingSettings.get_end_date(self.item, self.member, datetime.date(2022, 3, 30)))

    def test_more_handin_days(self):
        self.lending_settings.hand_in_days=6
        self.lending_settings.save()
        self.assertEqual(datetime.date(2022, 5, 10), LendingSettings.get_end_date(self.item, self.member, datetime.date(2022, 4, 4)))
