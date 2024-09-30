from django.contrib.auth.models import Group

from django.core.management.base import BaseCommand


from datamining.views import get_member_statistics



def number_shrinking(num):
    return int(str(float("0." + num)).split(".")[1])


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        get_member_statistics("2019-01-01")
