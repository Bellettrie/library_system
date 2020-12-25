import mysql.connector

from django.core.management.base import BaseCommand

from members.models import Member


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

            if member.should_be_anonymised():
                # print(member)
                counter += 1
                should_delete =  member.can_be_deleted() and member.privacy_period_ended()
                member.anonymise_me(dry_run=False)
                if should_delete:
                    member.delete()

        print(counter)
