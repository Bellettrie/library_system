import datetime

from django.test import TestCase

# Create your tests here.
from members.models import Member
from works.models import ItemType


class LendingCountTest(TestCase):
    def setUp(self):
        self.type1 = ItemType.objects.create(name="Type1", old_id=0)
        self.type2 = ItemType.objects.create(name="Type2", old_id=0)
        self.member = Member.objects.create(end_date=datetime.date(2023, 4, 4))
        self.member2 = Member.objects.create(end_date=None)

    def test_member_is_active(self):
        self.assertTrue(self.member.is_currently_member(datetime.date(2022, 1, 1)))
        self.assertFalse(self.member.is_currently_member(datetime.date(2024, 1, 1)))
        self.assertTrue(self.member2.is_currently_member(datetime.date(2024, 1, 1)))
