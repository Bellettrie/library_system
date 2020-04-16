import datetime
from django.test import TestCase
from members.models import Member, Committee


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


class MemberTestCase(TestCase):
    def setUp(self):
        self.committe1 = Committee.objects.create(
            name="openers",
            code="open",
            active_member_committee=True
        )
        self.committe2 = Committee.objects.create(
            name="testers",
            code="test",
            active_member_committee=False
        )
        self.member = Member.objects.create(
            name="Testname",
            nickname="Nickname",
            addressLineOne="Hollandstraat 66",
            addressLineTwo="6666 HL Enschede",
            addressLineThree="Holland",
            email="board@bellettrie.utwente.nl",
            phone="06 666 666 13 13",
            student_number="s123 456 789",
            end_date=datetime.date(2023, 4, 4),
            notes="",
            is_anonymous_user=False
        )
        self.member2 = Member.objects.create(
            name="Testname2",
            nickname="Nickname2",
            addressLineOne="Hollandstraat 66",
            addressLineTwo="6666 HL Enschede",
            addressLineThree="Holland",
            email="board@bellettrie.utwente.nl",
            phone="06 666 666 13 13",
            student_number="s123 456 789",
            end_date=datetime.date(2023, 4, 4),
            notes="",
            is_anonymous_user=False
        )
        self.member.committees.add(self.committe1)
        self.member.save()
        self.member2.committees.add(self.committe2)
        self.member2.save()

    def test_is_active_member(self):
        self.assertEqual(self.member.is_active(), True)

    def test_is_inactive_member(self):
        self.assertEqual(self.member2.is_active(), False)

    def test_become_active(self):
        self.assertEqual(self.member2.is_active(), False)
        self.member2.committees.add(self.committe1)
        self.member2.save()
        self.assertEqual(self.member2.is_active(), True)

    def test_become_inactive(self):
        self.assertEqual(self.member.is_active(), True)
        self.member.committees.remove(self.committe1)
        self.member.save()
        self.assertEqual(self.member.is_active(), False)
