from datetime import datetime
from random import randint

from django.db import models

# Create your models here.
from enum import Enum

from members.management.commands.namegen import generate_full_name, generate_name


class MemberType(Enum):
    CUSTOMER = 1
    ACTIVE = 2
    LENDER = 3
    ADMIN = 4


class Member(models.Model):
    name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255)
    addressLineOne = models.CharField(max_length=255)
    addressLineTwo = models.CharField(max_length=255)
    addressLineThree = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    student_number = models.CharField(max_length=32)
    membership_type_old = models.CharField(max_length=32)
    notes = models.CharField(max_length=1023)
    old_customer_type = models.CharField(max_length=64)
    old_id = models.IntegerField()
    is_anonymous_user = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True)

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
        members = Member.objects.filter(end_date__isnull=False).filter(end_date__lte=str(now.year-10)+ "-" + str(now.month)+ "-" + str(now.day))
        print(members)
        anonymous_members = Member.objects.filter(is_anonymous_user=True)

        for member in members:
            for lending in member.lending_set.all():
                lending.member = anonymous_members[0]
                lending.save()
            member.delete()

        print(anonymous_members[0].lending_set.all())




