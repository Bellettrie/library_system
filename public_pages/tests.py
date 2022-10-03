from datetime import date

from django.test import TestCase

# Create your tests here.
from members.models import Committee, Member, MembershipPeriod
from public_pages.models import PublicPage, PublicPageGroup
from public_pages.views import forbid_showing_page


class PublicPageRightsCheck(TestCase):
    def setUp(self):
        com = Committee.objects.create(name="testcommittee", code="TC", active_member_committee=True)
        com2 = Committee.objects.create(name="testcommittee2", code="TC2", active_member_committee=True)
        pg1 = PublicPageGroup.objects.create(name="testgroup", committees=com)
        self.pp1 = PublicPage.objects.create(name="test1", title="test1", text="", group=pg1)
        self.pp2 = PublicPage.objects.create(name="test2", title="test1", text="", group=pg1,
                                             only_for_logged_in=True)
        self.pp3 = PublicPage.objects.create(name="test2", title="test1", text="", group=pg1,
                                             only_for_current_members=True)
        self.pp4 = PublicPage.objects.create(name="test3", title="test1", text="", group=pg1)
        self.pp3.limited_to_committees.add(com2)
        self.member1 = Member.objects.create()
        MembershipPeriod.objects.create(member=self.member1, start_date=None, end_date="2022-02-02")

        self.member2 = Member.objects.create()
        MembershipPeriod.objects.create(member=self.member2, start_date=None, end_date="2025-02-02")

    def test_anyone_can_view(self):
        self.assertFalse(forbid_showing_page(self.pp1, False, self.member1))
        self.assertFalse(forbid_showing_page(self.pp1, True, self.member1))

    def test_only_logged_in(self):
        self.assertTrue(forbid_showing_page(self.pp2, True, self.member1))
        self.assertFalse(forbid_showing_page(self.pp2, False, self.member1))

    def test_only_currently_member(self):
        self.assertTrue(forbid_showing_page(self.pp3, True, self.member2, date(2022, 1, 1)))
        self.assertTrue(forbid_showing_page(self.pp3, True, self.member2, date(2024, 1, 1)))
