from django.core.management.base import BaseCommand

from members.models import Member, MembershipPeriod


class Command(BaseCommand):
    help = 'Delete members that should be deleted'

    def handle(self, *args, **options):
        counter = 0
        for member in Member.objects.all():
            if member.can_be_deleted() and member.reunion_period_ended():
                counter += 1
                MembershipPeriod.objects.filter(member=member).delete()

                member.delete()
