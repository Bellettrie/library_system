from django.core.management.base import BaseCommand

from members.models import Member, MemberLog


class Command(BaseCommand):
    help = 'Pseudonimises all membership data; removes log entries for old member data changes.'

    def handle(self, *args, **options):
        MemberLog.objects.all().delete()
        members = Member.objects.all()
        for member in members:
            member.pseudonymise()
