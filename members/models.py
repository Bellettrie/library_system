from datetime import datetime, timedelta
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import CASCADE, PROTECT, Q

from members.management.commands.namegen import generate_full_name

PAST = datetime.date(datetime.fromisoformat('1900-01-01'))
FUTURE = datetime.date(datetime.fromisoformat('2100-01-01'))

def overlaps(startA, endA, startB, endB):
    startA = startA or datetime.date(datetime.fromisoformat('1900-01-01'))
    startB = startB or datetime.date(datetime.fromisoformat('1900-01-01'))
    endA = endA or datetime.date(datetime.fromisoformat('2100-01-01'))
    endB = endB or datetime.date(datetime.fromisoformat('2100-01-01'))

    return (startA <= endB) and (endA >= startB)

class Committee(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    active_member_committee = models.BooleanField()

    def __str__(self):
        return self.name


class MemberBackground(models.Model):
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)
    old_str = models.CharField(max_length=64)

    def __str__(self):
        return self.visual_name


class MembershipType(models.Model):
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)
    old_str = models.CharField(max_length=64)
    needs_union_card = models.BooleanField(default=True)
    has_end_date = models.BooleanField(default=True)

    def __str__(self):
        return self.visual_name


class MemberData(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    addressLineOne = models.CharField(max_length=255)
    addressLineTwo = models.CharField(max_length=255)
    addressLineThree = models.CharField(max_length=255, blank=True)
    addressLineFour = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=64)
    student_number = models.CharField(max_length=32, blank=True)
    # end_date = models.DateField(null=True, blank=True)
    # start_date = models.DateField(null=True, blank=False, default="2020-09-01")
    is_blacklisted = models.BooleanField(default=False)
    # member_background = models.ForeignKey(MemberBackground, on_delete=PROTECT, null=True)
    # membership_type = models.ForeignKey(MembershipType, on_delete=PROTECT, null=True)

    notes = models.TextField(blank=True)


class Member(MemberData):
    membership_type_old = models.CharField(max_length=32)
    old_customer_type = models.CharField(max_length=64, null=True, blank=True)
    old_id = models.IntegerField(null=True, blank=True)
    is_anonymous_user = models.BooleanField(default=False)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    committees = models.ManyToManyField(Committee, blank=True)

    privacy_activities = models.BooleanField(default=False)
    privacy_publications = models.BooleanField(default=False)
    privacy_reunions = models.BooleanField(default=False)
    privacy_reunion_end_date = models.DateField(auto_now=True)

    invitation_code = models.CharField(max_length=64, null=True, blank=True)
    invitation_code_valid = models.BooleanField(default=False)

    is_anonimysed = models.BooleanField(default=False)

    class Meta:
        permissions = [('committee_update', 'Can update committee')]

    @property
    def start_date(self):
        start_date = datetime.fromisoformat("2100-01-01").date()
        for z in MembershipPeriod.objects.filter(member=self):
            if z.start_date is None or start_date is None or z.start_date < start_date:
                start_date = z.start_date
        return start_date

    @property
    def end_date(self):
        end_date = datetime.fromisoformat("1900-01-01").date()
        for z in MembershipPeriod.objects.filter(member=self):
            if z.end_date is None or end_date is None or z.end_date > end_date:
                end_date = z.end_date

            # return None
        return end_date

    @property
    def membership_type(self):
        period = self.get_current_membership_period()
        if period is not None:
            return period.membership_type

    def has_reservations(self):
        from lendings.models import Reservation

        return len(Reservation.objects.filter(member=self)) > 0

    def get_current_membership_period(self, current_date=None):
        current_date = current_date or datetime.date(datetime.now())
        for period in MembershipPeriod.objects.filter(member=self):
            if (period.start_date is None or period.start_date < current_date) and (period.end_date is None or current_date < period.end_date):
                return period
        return None

    def is_currently_member(self, current_date=None):
        return self.get_current_membership_period(current_date) is not None

    def can_lend_item_type(self, item_type, current_date=None):
        from lendings.models import Lending, Reservation
        from works.models import ItemType, Category

        lendings = Lending.objects.filter(member=self, item__location__category__item_type=item_type, handed_in=False)
        reservations = Reservation.objects.filter(member=self, reservation_end_date__gt=datetime.now()) | Reservation.objects.filter(member=self, reservation_end_date__isnull=True)
        from config.models import LendingSettings
        return (len(lendings) + len(reservations)) < LendingSettings.get_max_count(item_type, self)

    def has_late_items(self, current_date=None):
        current_date = current_date or datetime.date(datetime.now())

        from lendings.models import Lending
        from works.models import ItemType, Category

        lendings = Lending.objects.filter(member=self, handed_in=False)

        for lending in lendings:
            if lending.is_late(current_date):
                return True
        return False

    def is_active(self):
        for committee in self.committees.all():
            if committee.active_member_committee:
                return True
        return False

    def save(self, *args, **kwargs):
        MemberLog.from_member(self)
        super().save(*args, **kwargs)


    def try_and_delete_double_periods(self):
        to_delete = set()

        for msp in MembershipPeriod.objects.filter(member=self):
            for msp2 in MembershipPeriod.objects.filter(member=self):
                if msp != msp2 and msp2 not in to_delete and msp not in to_delete and overlaps(msp.start_date, msp.end_date, msp2.start_date, msp2.end_date):
                    if msp.member_background == msp2.member_background and msp.membership_type == msp2.membership_type:
                        msp.start_date = min(msp.start_date or FUTURE, msp2.start_date or FUTURE)

                        msp.end_date = max(msp.end_date or FUTURE, msp2.end_date or FUTURE)
                        if msp.start_date == FUTURE:
                            msp.start_date = None
                        if msp.end_date == FUTURE:
                            msp.end_date = None
                        msp.save()
                        to_delete.add(msp2)
                    else:
                        if msp.start_date < msp2.start_date:
                            msp.end_date = msp2.start_date
                        else:
                            msp2.end_date = msp.start_date
                        msp.save()
                        msp2.save()
                        if msp.end_date and msp.start_date >= msp.end_date:
                            to_delete.add(msp)
                        if msp2.end_date and msp2.start_date >= msp2.end_date:
                            to_delete.add(msp2)
        for z in to_delete:
            z.delete()
    def __str__(self):
        return self.name

    def pseudonymise(self):
        self.name = generate_full_name()
        self.nickname = ""
        self.addressLineOne = "Hollandstraat 66"
        self.addressLineTwo = "6666 HL Enschede"
        self.addressLineThree = "Holland"
        self.phone = "06 666 666 13 13"
        self.email = "board@bellettrie.utwente.nl"
        self.student_number = "s123 456 789"
        self.notes = "free member"
        self.save()

    def destroy(self, filter_list, field, anonymous_members, dry_run):
        import random

        for z in filter_list:
            setattr(z, field, random.sample(anonymous_members, 1)[0])
            if not dry_run:
                z.save()

    def anonymise_me(self, dry_run=True):
        anonymous_members = list(Member.objects.filter(is_anonymous_user=True))
        from mail.models import MailLog
        from lendings.models import Lending
        from ratings.models import Rating
        self.destroy(Lending.objects.filter(member=self), 'member', anonymous_members, dry_run)
        self.destroy(Lending.objects.filter(lended_by=self), 'lended_by', anonymous_members, dry_run)
        self.destroy(Lending.objects.filter(handed_in_by=self), 'handed_in_by', anonymous_members, dry_run)

        from lendings.models import Reservation
        self.destroy(Reservation.objects.filter(member=self), 'member', anonymous_members, dry_run)
        self.destroy(Reservation.objects.filter(reserved_by=self), 'reserved_by', anonymous_members, dry_run)
        self.destroy(MailLog.objects.filter(member=self), 'member', anonymous_members, dry_run)
        self.destroy(MembershipPeriod.objects.filter(member=self), 'member', anonymous_members, dry_run)
        self.destroy(Rating.objects.filter(member=self), 'member', anonymous_members, dry_run)
        if not dry_run:
            self.is_anonimysed = True
            self.addressLineOne = "-"
            self.addressLineTwo = "-"
            self.addressLineThree = "-"
            self.addressLineFour = "-"
            self.student_number = "-"
            self.old_customer_type = None
            self.notes = "-"
            self.old_id = None
            self.membership_type_old = "-"
            self.phone = "-"
            self.save()

    @staticmethod
    def anonymise_people():
        now = datetime.now()
        members = Member.objects.filter(end_date__isnull=False).filter(
            end_date__lte=str(now.year - 10) + "-" + str(now.month) + "-" + str(now.day))

        for member in members:
            if member.should_be_anonymised():
                member.anonymise_me(dry_run=False)
                member.delete()

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

    def get_periods(self):
        return self.membershipperiod_set.all().order_by('start_date')

    def privacy_period_ended(self):
        if self.is_anonimysed and not self.privacy_reunions:
            return True
        now = datetime.now().date()
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
        from lendings.models import Reservation
        if len(Reservation.objects.filter(Q(member=self) | Q(reserved_by=self))) > 0:
            return False
        from ratings.models import Rating
        if len(Rating.objects.filter(member=self)) > 0:
            return False

        return True

    def should_be_anonymised_reason(self, now=None):
        if now is None:
            now = datetime.now().date()
        if self.is_anonimysed:
            return "Already anonymised"
        if self.is_blacklisted:
            return "Is blacklisted"
        if self.end_date is None:
            return "Member is a special member."
        if self.is_currently_member():
            return "Is currently a member."
        if self.is_active():
            return "Member is still active"
        if self.user is not None and (self.user.last_login.date() - now).days < -400:
            return "Logged in recently;  will be anonymised in " + str(400 - (self.user.last_login.date() - now).days) + " days."
        if (now - self.end_date).days < 800:
            return "Was recently a member; will be anonymised in " + str(800 - (now - self.end_date).days) + " days."
        from lendings.models import Lending
        if len(Lending.objects.filter(member=self, handed_in=False)) > 0:
            return "Still has a book lent."
        a = now - timedelta(days=180)
        print(a)
        if len(Lending.objects.filter(member=self, handed_in_on__gte="2020-01-01")):
            return "Recently lent a book"
        from lendings.models import Reservation
        if len(Reservation.objects.filter(Q(member=self))) > 0:
            return "Still has a reservation"

        return None

    def should_be_anonymised(self, now=None):
        if now is None:
            now = datetime.now().date()
        return self.should_be_anonymised_reason(now=now) is None


class MemberLog(MemberData):
    date_edited = models.DateTimeField(auto_now=True)

    @staticmethod
    def from_member(member: Member):
        data = MemberLog()
        data.name = member.name
        data.nickname = member.nickname
        data.addressLineOne = member.addressLineOne
        data.addressLineTwo = member.addressLineTwo
        data.addressLineThree = member.addressLineThree
        data.addressLineFour = member.addressLineFour
        data.email = member.email
        data.phone = member.phone
        data.student_number = member.student_number
        # data.end_date = member.end_date
        data.notes = member.notes
        # data.start_date = member.start_date
        data.save()


class MembershipPeriod(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT, null=True)
    start_date = models.DateField(null=True, blank=False)
    end_date = models.DateField(null=True, blank=True)
    member_background = models.ForeignKey(MemberBackground, on_delete=PROTECT, null=True)
    membership_type = models.ForeignKey(MembershipType, on_delete=PROTECT, null=True)
