from django.core.management.base import BaseCommand

from members.models import Member


class Command(BaseCommand):
    help = 'Pseudonimises all membership data; removes log entries for old member data changes.'

    def handle(self, *args, **options):
        members = Member.objects.all()
        for member in members:
            member.pseudonymise()
