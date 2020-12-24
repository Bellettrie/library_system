import datetime
from django.contrib.auth.models import User, Group

from django.test import TestCase
from members.models import Member, Committee, MembershipPeriod
from works.models import ItemType


class LendingCountTest(TestCase):
    def setUp(self):
        self.type1 = ItemType.objects.create(name="Type1", old_id=0)
        self.type2 = ItemType.objects.create(name="Type2", old_id=0)
        self.member = Member.objects.create()
        MembershipPeriod.objects.create(member=self.member, start_date=None, end_date="2022-02-02")

        self.member2 = Member.objects.create()
        MembershipPeriod.objects.create(member=self.member2, start_date=None, end_date="2025-02-02")

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

        self.group1 = Group.objects.create(name="open")
        self.group2 = Group.objects.create(name="test")

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
            notes="",
            is_anonymous_user=False
        )
        self.member3 = Member.objects.create(
            name="Testname3",
            nickname="Nickname2",
            addressLineOne="Hollandstraat 66",
            addressLineTwo="6666 HL Enschede",
            addressLineThree="Holland",
            email="board@bellettrie.utwente.nl",
            phone="06 666 666 13 13",
            student_number="s123 456 789",
            notes="",
            is_anonymous_user=False
        )
        self.user1 = User.objects.create()

        self.member.committees.add(self.committe1)
        self.member.user = self.user1
        self.member.update_groups()
        self.member.save()
        self.member2.committees.add(self.committe2)
        self.member2.update_groups()
        self.member2.save()

    def test_is_active_member(self):
        self.assertEqual(self.member.is_active(), True)

    def test_is_inactive_member(self):
        self.assertEqual(self.member2.is_active(), False)

    def test_become_active(self):
        self.assertEqual(self.member2.is_active(), False)
        self.member2.committees.add(self.committe1)
        self.member2.update_groups()
        self.member2.save()
        self.assertEqual(self.member2.is_active(), True)

    def test_become_inactive(self):
        self.assertEqual(self.member.is_active(), True)
        self.member.committees.remove(self.committe1)
        self.member.update_groups()
        self.member.save()
        self.assertEqual(self.member.is_active(), False)

    def test_starts_with_correct_committee(self):
        self.assertIsNotNone(self.member.user)
        self.assertEqual(1, self.member.user.groups.all().__len__())
        self.assertEqual("open", self.member.user.groups.first().name)

    def test_correct_rights_when_adding_user(self):
        self.user2 = User.objects.create(username="Bob")
        self.member2.user = self.user2
        self.member2.save()
        self.member2.update_groups()
        self.assertEqual(1, self.member2.user.groups.all().__len__())

    def test_removing_committee(self):
        self.member.committees.clear()
        self.member.update_groups()
        self.member.save()
        self.assertEqual(0, self.member.user.groups.all().__len__())
