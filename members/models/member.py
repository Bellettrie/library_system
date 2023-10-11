import sys
from datetime import datetime, timedelta

from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import CASCADE, Q

from members.management.commands.namegen import generate_full_name
from members.models.committee import Committee
from members.models.member_data import MemberData
from members.models.membership_period import MembershipPeriod
from utils.time import get_today

if sys.version_info.minor < 8:
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()


class Member(MemberData):
    is_anonymous_user = models.BooleanField(default=False)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    committees = models.ManyToManyField(Committee, blank=True)

    privacy_activities = models.BooleanField(default=False)
    privacy_publications = models.BooleanField(default=False)
    privacy_reunions = models.BooleanField(default=False)
    privacy_reunion_end_date = models.DateField(auto_now=True)

    invitation_code = models.CharField(max_length=64, null=True, blank=True)
    invitation_code_end_date = models.DateTimeField(null=True, blank=True)

    invitation_code_valid = models.BooleanField(default=False)

    dms_registered = models.BooleanField(default=False)
    is_anonimysed = models.BooleanField(default=False)

    class Meta:
        permissions = [('committee_update', 'Can update committee')]

    def save(self, *args, **kwargs):
        from members.models.member_log import MemberLog
        super().save(*args, **kwargs)
        MemberLog.from_member(self)

    def __str__(self):
        return self.name

    def last_end_date(self):
        end_date = None
        for period in self.get_periods():
            if period.end_date:
                end_date = max(end_date or period.end_date, period.end_date)
            else:
                return None
        return end_date

    def get_current_membership_period(self, current_date: datetime.date = None):
        current_date = current_date or get_today()
        for period in MembershipPeriod.objects.filter(member=self):
            if (period.start_date is None or period.start_date <= current_date) and (
                    period.end_date is None or current_date <= period.end_date):
                return period
        return None

    def get_periods(self):
        return self.membershipperiod_set.all().order_by('start_date')

    @property
    def membership_type(self):
        period = self.get_current_membership_period()
        if period is not None:
            return period.membership_type

    def has_reservations(self):
        from reservations.models import Reservation
        return len(Reservation.objects.filter(member=self)) > 0

    def is_currently_member(self, current_date=None):
        return self.get_current_membership_period(current_date) is not None

    def is_active(self):
        for committee in self.committees.all():
            if committee.active_member_committee:
                return True
        return False

    def pseudonymise(self):
        self.name = generate_full_name()
        self.addressLineOne = "Hollandstraat 66"
        self.nickname = ""
        self.addressLineTwo = "6666 HL Enschede"
        self.addressLineThree = "Holland"
        self.phone = "06 666 666 13 13"
        self.email = "board@bellettrie.utwente.nl"
        self.student_number = "s123 456 789"
        self.notes = "free member"
        self.save()

    def update_groups(self):
        if self.user is not None:
            committees = self.committees.all()
            groups = self.user.groups.all()
            for group in groups:
                found = False
                for committee in committees:
                    found = found or committee.code == group.name
                if not found:
                    self.user.groups.remove(group)
            for committee in committees:
                found = False
                for group in groups:
                    found = found or committee.code == group.name
                if not found:
                    self.user.groups.add(Group.objects.get(name=committee.code))
            self.user.save()

    def reunion_period_ended(self):
        if self.is_anonimysed and not self.privacy_reunions:
            return True
        now = get_today()
        if self.privacy_reunions:
            if (now - self.privacy_reunion_end_date).days < 8000:
                return False
        else:
            if (now - self.privacy_reunion_end_date).days < 800:
                return False
        return True

    def can_be_deleted(self):
        from lendings.models import Lending
        if len(Lending.objects.filter(Q(lended_by=self) | Q(handed_in_by=self) | Q(member=self))) > 0:
            return False
        from reservations.models import Reservation
        if len(Reservation.objects.filter(Q(member=self) | Q(reserved_by=self))) > 0:
            return False
        return True

    def should_be_anonymised(self, now=None):
        if now is None:
            now = get_today()
        from members.procedures.anonymise import can_be_anonymised
        return can_be_anonymised(self, now)
