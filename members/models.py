from datetime import datetime
from random import randint

from django.contrib.auth.models import User, Group
from django.db import models

# Create your models here.
from enum import Enum

from django.db.models import CASCADE

from members.management.commands.namegen import generate_full_name, generate_name


class Committee(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64)
    active_member_committee = models.BooleanField()

    def __str__(self):
        return self.name


class Member(models.Model):
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    addressLineOne = models.CharField(max_length=255)
    addressLineTwo = models.CharField(max_length=255)
    addressLineThree = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    student_number = models.CharField(max_length=32)
    membership_type_old = models.CharField(max_length=32)
    notes = models.CharField(max_length=1023)
    old_customer_type = models.CharField(max_length=64, null=True, blank=True)
    old_id = models.IntegerField(null=True, blank=True)
    is_anonymous_user = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    committees = models.ManyToManyField(Committee)

    def is_active(self):
        for committee in self.committees.all():
            if committee.active_member_committee:
                return True
        return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

    def pseudonymise(self):
        self.name = generate_full_name()
        self.nickname = ""
        self.addressLineOne = generate_name() + " " + str(randint(1, 100))
        self.addressLineTwo = generate_name()
        self.addressLineThree = generate_name()
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
            self.user.groups.clear()

            for c in self.committees.all():
                g = Group.objects.get(name=c.code)
                self.user.groups.add(g)
            self.user.save()
