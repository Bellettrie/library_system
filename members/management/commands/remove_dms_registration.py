from django.core.management.base import BaseCommand


from members.procedures.dms_purge import dms_purge


class Command(BaseCommand):
    help = "sets dms_registered=false members if membership end date is reached"

    def handle(self, *args, **options):
        dms_purge()
