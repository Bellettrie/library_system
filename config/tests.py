import datetime

from django.test import TestCase

# Create your tests here.
from config.models import Holiday, LendingSettings
from works.models import ItemType, Location, Category

""" Start date: 28 february 2022 
    mo | tu | we | th | fr | sa | su
    28 | 01 |[02 | 03 | 04]| 05 | 06
    07 | 08 | 08 | 10 | 11 | 12 | 13
    14 |[15 |{16]| 17}| 18 | 19 | 20
   [21 | 22 | 23 | 24 | 25]| 26 | 27
    28 |[29 | 30 | 31]| 31 | 01 | 02"""


class HolidayTestCase(TestCase):
    def setUp(self):
        Holiday.objects.create(name="1", starting_date=datetime.date(2022, 3, 2),
                               ending_date=datetime.date(2022, 3, 4))
        Holiday.objects.create(name="2", starting_date=datetime.date(2022, 3, 15),
                               ending_date=datetime.date(2022, 3, 16))
        Holiday.objects.create(name="3", starting_date=datetime.date(2022, 3, 16),
                               ending_date=datetime.date(2022, 3, 17))
        Holiday.objects.create(name="4", starting_date=datetime.date(2022, 3, 21),
                               ending_date=datetime.date(2022, 3, 25))
        Holiday.objects.create(name="4", starting_date=datetime.date(2022, 3, 29),
                               ending_date=datetime.date(2022, 3, 31))

    def test_before_day_not_in_holiday(self):
        date = datetime.date(2022, 3, 1)
        self.assertEqual(Holiday.get_handin_day_before_or_on(date), date)

    def test_after_day_not_in_holiday(self):
        date = datetime.date(2022, 3, 1)
        self.assertEqual(Holiday.get_handin_day_after_or_on(date), date)

    def test_before_weekend(self):
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 12)), datetime.date(2022, 3, 11))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 13)), datetime.date(2022, 3, 11))

    def test_after_weekend(self):
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 12)), datetime.date(2022, 3, 14))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 13)), datetime.date(2022, 3, 14))

    def test_before_holiday(self):
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 15)), datetime.date(2022, 3, 14))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 16)), datetime.date(2022, 3, 14))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 17)), datetime.date(2022, 3, 14))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 29)), datetime.date(2022, 3, 28))

    def test_after_holiday(self):
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 15)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 16)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 17)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 31)), datetime.date(2022, 4, 1))

    def test_before_holiday_weekend(self):
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 19)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 21)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 23)), datetime.date(2022, 3, 18))
        self.assertEqual(Holiday.get_handin_day_before_or_on(datetime.date(2022, 3, 25)), datetime.date(2022, 3, 18))

    def test_after_holiday_weekend(self):
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 3)), datetime.date(2022, 3, 7))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 19)), datetime.date(2022, 3, 28))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 21)), datetime.date(2022, 3, 28))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 23)), datetime.date(2022, 3, 28))
        self.assertEqual(Holiday.get_handin_day_after_or_on(datetime.date(2022, 3, 25)), datetime.date(2022, 3, 28))


class LendingSettingsBase(TestCase):
    book = None
    comic = None
    a = None
    b = None
    c = None

    def lending_settings_create(self):
        self.book = ItemType.objects.create(name="Book")
        self.comic = ItemType.objects.create(name="Comic")

        self.a = LendingSettings.objects.create(item_type=self.book,
                                                member_is_active=True,
                                                fine_amount=50,
                                                max_fine=500,
                                                max_count=5,
                                                borrow_money=0,
                                                extend_count=2,
                                                term=21)
        self.b = LendingSettings.objects.create(item_type=self.book,
                                                member_is_active=False,
                                                fine_amount=50,
                                                max_fine=500,
                                                max_count=10,
                                                borrow_money=0,
                                                extend_count=2,
                                                term=41)
        self.c = LendingSettings.objects.create(item_type=self.comic,
                                                member_is_active=False,
                                                fine_amount=70,
                                                max_fine=700,
                                                max_count=10,
                                                borrow_money=20,
                                                extend_count=0,
                                                term=7)


class LendingSettingsTestCase(LendingSettingsBase):
    def setUp(self):
        self.lending_settings_create()

    def test_lending_settings_get_for_inactive(self):
        self.assertEqual(LendingSettings.get_for_type(self.book, False), self.b)
        self.assertEqual(LendingSettings.get_for_type(self.comic, False), self.c)

    def test_lending_settings_get_for_active_with_active(self):
        self.assertEqual(LendingSettings.get_for_type(self.book, True), self.a)

    def test_lending_settings_get_for_active_without_active(self):
        self.assertEqual(LendingSettings.get_for_type(self.comic, True), self.c)
