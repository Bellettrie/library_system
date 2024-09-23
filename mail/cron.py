from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from utils.time import get_today


class SendSingleEmail(CronJobBase):
    RUN_EVERY_MINS = 0  # Run every time

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'mail.send_single_email'  # a unique code

    def do(self):
        for mail in MailLog.objects.filter(sent=False):
            mail.send()
            return
