from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from reservations.procedures.clear_crons import clear_old_reservations, clear_unavailable, clear_not_member, \
    set_end_date_if_no_lent_out
from utils.time import get_today


class ReservationCancel:
    def exec(self):
        clear_old_reservations()
        clear_unavailable()
        clear_not_member()
        set_end_date_if_no_lent_out()
