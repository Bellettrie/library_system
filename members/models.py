from django.db import models

# Create your models here.
from enum import Enum


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
