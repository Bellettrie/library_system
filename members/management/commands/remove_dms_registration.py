from django.core.management.base import BaseCommand

from members.models import Member, MembershipPeriod
from members.procedures.dms_purge import dms_purge
from utils.time import get_today


class Command(BaseCommand):
    help = "sets dms_registered=false members if membership end date is reached"

    def handle(self, *args, **options):
        dms_purge()
