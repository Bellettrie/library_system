from datetime import datetime

from django.test import TestCase

# Create your tests here.
from config.tests import BasicTestCase
from lendings.models import Lending
from works.models import Item


class LendingPreLendingTestCase(BasicTestCase):

    def setUp(self):
        super().setUp()
        self.item2 = Item.objects.create(publication=self.publication, old_id=0, hidden=False, location=self.location)
        Lending.create_lending(self.item2, self.member, self.member, datetime.date(datetime.fromisoformat("2020-02-02")))

    def test_item_available(self):
        self.assertTrue(self.item.is_available())
        self.assertFalse(self.item2.is_available())

    def test_return_book(self):
        self.item2.current_lending().register_returned(self.member, datetime.date(datetime.fromisoformat("2020-03-02")))
        self.assertTrue(self.item2.is_available())
