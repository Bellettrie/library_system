from django.core.management.base import BaseCommand, CommandError
from members.models import Member, Committee


def get_name(x):
    vn = x.get("voornaam")
    if len(vn) == 0:
        return x.get("naam")
    return vn + " " + x.get("naam")


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for member in Member.objects.all():
            member.update_groups()
