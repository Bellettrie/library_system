from datetime import datetime, timedelta

from django.db import models

# Create your models here.
from django.db.models import PROTECT
from django.utils import timezone

from mail.models import mail_member
from members.models import Member
from datetime import date


class Lending(models.Model):
    class Meta:
        permissions = [('extend', 'Can extend lending'),
                       ('extend_with_fine', 'Extend book even though it has a fine'),
                       ('return', 'Return book')]

    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    lended_on = models.DateField()
    lended_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="lended_out", null=True, blank=True)
    times_extended = models.IntegerField(default=0)
    last_extended = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    handed_in = models.BooleanField()
    handed_in_on = models.DateField(null=True, blank=True)
    handed_in_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="handed_in", null=True, blank=True)
    start_date = models.DateField(default=date.today)
    last_mailed = models.DateTimeField(default="1900-01-01")

    # This flag will be used to differentiate between having mailed for being almost too late, and having mailed for being late.
    # Almost-too-late is not implemented yet.
    mailed_for_late = models.BooleanField(default=False)

    def is_simple_extendable(self, now=None):
        if now is None:
            now = datetime.date(datetime.now())

        return not self.handed_in and now <= self.end_date

    def is_extendable(self, get_fine, now=None):
        return self.is_simple_extendable(now) | get_fine

    def is_at_extend_limit(self):
        from config.models import LendingSettings
        return self.times_extended < LendingSettings.get_extend_count(self.item.location.category.item_type,
                                                                      self.member)

    def is_late(self, now=None):
        if now is None:
            now = datetime.date(datetime.now())
        return now > self.end_date

    def is_almost_late(self, now=None):
        if now is None:
            now = datetime.date(datetime.now())
        return self.end_date - timedelta(minutes=4) < now

    def calculate_fine(self):
        from config.models import LendingSettings
        return format(LendingSettings.get_fine(self.item, self.member, self.end_date) / 100, '.2f')

    def extend(self, member: Member, now=None):
        if now is None:
            now = datetime.date(datetime.now())
        self.end_date = Lending.calc_end_date(self.member, self.item, now)
        self.last_extended = now
        self.times_extended = self.times_extended + 1
        self.save()

    def register_returned(self, member: Member, now=None):
        if now is None:
            now = datetime.date(datetime.now())
        self.handed_in = True
        self.handed_in_on = now
        self.handed_in_by = member
        self.save()
        self.item.is_seen("Book was returned")

    @staticmethod
    def create_lending(item, member: Member, edited_member: Member, now=None):
        if member.is_anonymous_user:
            raise ValueError("Member is an anonymous user")
        from works.models import Item
        if now is None:
            now = datetime.date(datetime.now())
        new_lending = Lending()
        new_lending.end_date = Lending.calc_end_date(member, item, now)
        new_lending.member = member
        new_lending.item = item
        new_lending.lended_on = datetime.now()
        new_lending.last_extended = datetime.now()
        new_lending.handed_in = False
        new_lending.lended_by = edited_member
        new_lending.save()
        item.is_seen("Book was lent out.")
        return new_lending

    @staticmethod
    def calc_end_date(member, item, now=None):
        if now is None:
            now = datetime.date(datetime.now())
        from config.models import LendingSettings
        return LendingSettings.get_end_date(item, member, now)

    @staticmethod
    def late_mails(fake=False):
        lendings = Lending.objects.filter(handed_in=False)
        late_dict = dict()
        almost_late_dict = dict()
        for lending in lendings:
            if not lending.mailed_for_late or lending.last_mailed + timedelta(minutes=7) < timezone.now():
                if lending.is_late():
                    my_list = late_dict.get(lending.member, [])
                    my_list.append(lending)
                    late_dict[lending.member] = my_list
                elif lending.is_almost_late() and lending.last_mailed + timedelta(minutes=7) < timezone.now():
                    print("HERE")
                    my_list = almost_late_dict.get(lending.member, [])
                    my_list.append(lending)
                    almost_late_dict[lending.member] = my_list

        for member in list(set(late_dict.keys()) | set(almost_late_dict.keys())):

            if not fake:
                late_list = late_dict.get(member, [])
                almost_late_list = almost_late_dict.get(member, [])
                mail_member('mails/late_mail.tpl',
                            {'member': member, 'has_late': len(late_list) > 0,
                             'has_nearly_late': len(almost_late_list) > 0, 'lendings': late_list,
                             'almost_late': almost_late_list}, member, True)
                for lending in late_list:
                    lending.last_mailed = timezone.now()

                    lending.mailed_for_late = True
                    lending.save()
                for lending in late_list:
                    lending.last_mailed = timezone.now()

                    lending.save()
        return almost_late_dict


class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=PROTECT)
    item = models.ForeignKey("works.Item", on_delete=PROTECT)
    reserved_on = models.DateField()
    reserved_by = models.ForeignKey(Member, on_delete=PROTECT, related_name="reservation_action_by")
    reservation_end_date = models.DateField(null=True, blank=True)
