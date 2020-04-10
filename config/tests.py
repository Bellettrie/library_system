import datetime

from django.test import TestCase

# Create your tests here.
from config.models import Holiday, LendingSettings
from members.models import Member
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
        self.member = Member.objects.create(end_date=datetime.date(2021, 4, 4))

    def test_holiday_one_day(self):
        self.assertEqual(datetime.date(2019, 1, 2), LendingSettings.get_end_date(self.item, self.member, datetime.date(2018, 12, 31 - 6)))
