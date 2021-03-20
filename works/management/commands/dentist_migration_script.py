from django.core.management.base import BaseCommand

from lendings.models import Lending
from members.models import Member
from works.models import ItemState


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        dentist = Member.objects.get(old_id=1137)

        for lending in Lending.objects.filter(member=dentist):
            print(lending.item.get_title(), lending.member.name, lending.handed_in_on)
            ItemState.objects.create(dateTime=lending.lended_on,type="OFFSITE", reason="Dentist", item=lending.item)
            if lending.handed_in_on is not None:
                ItemState.objects.create(dateTime=lending.handed_in_on, type="AVAILABLE", item=lending.item)
            lending.delete()