import mysql.connector

from django.core.management.base import BaseCommand

from members.models import Member, MembershipPeriod


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        counter = 0
        for member in Member.objects.all():

            if member.can_be_deleted() and member.reunion_period_ended():
                counter += 1
                MembershipPeriod.objects.filter(member=member).delete()

                member.delete()

        print(counter)
