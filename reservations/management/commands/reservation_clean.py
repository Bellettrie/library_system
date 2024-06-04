from django.core.management.base import BaseCommand
from reservations.procedures.clear_crons import clear_old_reservations, clear_unavailable, clear_not_member, \
    set_end_date_if_no_lent_out


class Command(BaseCommand):
    help = 'clean reservations'

    def handle(self, *args, **options):
        clear_old_reservations()
        clear_unavailable()
        clear_not_member()
        set_end_date_if_no_lent_out()
