from django.core.management.base import BaseCommand
from members.models import Member


class Command(BaseCommand):
    help = 'Fix some grouping issues by resetting the group status of all members'

    def handle(self, *args, **options):
        for member in Member.objects.all():
            member.update_groups()
