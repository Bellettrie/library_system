from datetime import datetime

from django.test import TestCase

# Create your tests here.
# from config.tests import BasicTestCase
from lendings.models import Lending
from lendings.procedures.new_lending import create_lending
from works.models import Item

#
# class LendingPreLendingTestCase(BasicTestCase):
#
#     def setUp(self):
#         super().setUp()
#         self.item2 = Item.objects.create(publication=self.publication, old_id=0, hidden=False, location=self.location)
#         self.lending = create_lending(self.item2, self.member, self.member, datetime.date(datetime.fromisoformat("2020-02-02")))
#
#     def test_item_available(self):
#         self.assertTrue(self.item.is_available_for_lending())
#         self.assertFalse(self.item2.is_available_for_lending())
#
#     def test_return_book(self):
#         self.item2.current_lending().register_returned(self.member, datetime.date(datetime.fromisoformat("2020-03-02")))
#         self.assertTrue(self.item2.is_available_for_lending())
#
#     def test_late_items(self):
#         self.assertTrue(self.member.has_late_items(datetime.date(datetime.fromisoformat("2021-02-02"))))
#         self.assertFalse(self.member.has_late_items(datetime.date(datetime.fromisoformat("2020-02-03"))))
#
#     def test_extend_lending(self):
#         self.assertTrue(self.lending.is_late(datetime.date(datetime.fromisoformat("2021-02-03"))))
#         self.lending.extend(self.member, datetime.date(datetime.fromisoformat("2021-02-03")))
#         self.assertFalse(self.lending.is_late(datetime.date(datetime.fromisoformat("2021-02-04"))))
#
#     def test_can_extend(self):
#         self.assertTrue(self.lending.is_extendable(False, datetime.date(datetime.fromisoformat("2020-02-03"))))
#         self.assertFalse(self.lending.is_extendable(False, datetime.date(datetime.fromisoformat("2021-02-03"))))
