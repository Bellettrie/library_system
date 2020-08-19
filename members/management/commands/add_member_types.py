from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand

from members.models import Committee, MemberBackground, MembershipType, Member
from members.permissions import KASCO, BOARD, ADMIN, COMCO, BOOKBUYERS, KICKIN, LENDERS, BOOKS, WEB, KONNICHIWA, RETRIEVAL

"""
class MemberBackground(models.Model):
    old_str = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)


class MembershipType(models.Model):
    old_str = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    visual_name = models.CharField(max_length=64)
    fee = models.IntegerField(default=0)
    needs_union_card = models.BooleanField(default=True)

"""


class Command(BaseCommand):
    help = 'Add Membership types'

    def handle(self, *args, **options):
        membership_backgrounds = [('andere', 'other', 'Other'),
                                  ('student UT', 'student', 'Student UT'),
                                  ('medewerker UT', 'employee', 'Employee UT'),
                                  ('student HE', 'saxion', 'Saxion Student'),
                                  ]
        membership_types = [
            ('gewoon lid', 'member', 'Regular Member', True),
            ('lid van verdienste', 'verdienste', 'Lid van Verdienste', False),
            ('erelid', 'erelid', 'Erelid', False),
        ]
        for m in Member.objects.all():
            m.membership_type = None
            m.member_background = None
            m.save()
        MemberBackground.objects.all().delete()
        MembershipType.objects.all().delete()
        for membership_background in membership_backgrounds:
            MemberBackground.objects.create(old_str=membership_background[0], name=membership_background[1], visual_name=membership_background[2])
        for membership_type in membership_types:
            MembershipType.objects.create(old_str=membership_type[0], name=membership_type[1], visual_name=membership_type[2], needs_union_card=membership_type[3], has_end_date=membership_type[3])
