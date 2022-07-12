from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from reservations.procedures.clear_crons import clear_old_reservations, clear_unavailable
from utils.time import get_today


class ReservationCancel(CronJobBase):
    RUN_EVERY_MINS = 60 * 24  # Run every time

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'reservations.cancel'  # a unique code

    def do(self):
        clear_old_reservations()
        clear_unavailable()
