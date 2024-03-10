from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from reservations.procedures.clear_crons import clear_old_reservations, clear_unavailable, clear_not_member, \
    set_end_date_if_no_lent_out
from utils.time import get_today


class ReservationCancel(CronJobBase):
    RUN_EVERY_MINS = 24*60  # Run every day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reservations.cancel'  # a unique code

    def do(self):
        clear_old_reservations()
        clear_unavailable()
        clear_not_member()
        set_end_date_if_no_lent_out()
