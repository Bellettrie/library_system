from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import CASCADE, PROTECT

from members.management.commands.namegen import generate_full_name


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
    end_date = models.DateField(null=True, blank=True)
    is_blacklisted = models.BooleanField(default=False)
    member_background = models.ForeignKey(MemberBackground, on_delete=PROTECT, null=True)
    membership_type = models.ForeignKey(MembershipType, on_delete=PROTECT, null=True)

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

    class Meta:
        permissions = [('committee_update', 'Can update committee')]

    def has_reservations(self):
        from lendings.models import Reservation

        return len(Reservation.objects.filter(member=self)) > 0

    def is_currently_member(self, current_date=None):
        current_date = current_date or datetime.date(datetime.now())
        return self.end_date is None or current_date < self.end_date

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
        if self.membership_type:
            if not self.membership_type.has_end_date:
                self.end_date = None
            elif self.end_date is None:
                print(self.name)
                print(self.old_id)
                raise ValueError("Member has to have an end date for this membership type")
        super().save(*args, **kwargs)

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

    @staticmethod
    def anonymise_people():
        now = datetime.now()
        members = Member.objects.filter(end_date__isnull=False).filter(
            end_date__lte=str(now.year - 10) + "-" + str(now.month) + "-" + str(now.day))
        anonymous_members = Member.objects.filter(is_anonymous_user=True)

        for member in members:
            for lending in member.lending_set.all():
                lending.member = anonymous_members[0]
                lending.save()
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
        data.end_date = member.end_date
        data.notes = member.notes
        data.save()
