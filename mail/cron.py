from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from utils.time import get_today


class SendSingleEmail(CronJobBase):
    RUN_EVERY_MINS = 0 # Run every time

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'mail.send_single_email'  # a unique code

    def do(self):
        for mail in MailLog.objects.filter(sent=False):
            mail.send()
            return


class CleanMailLog(CronJobBase):
    RUN_EVERY_MINS = 60*6 # Run 4 times per day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'mail.cleanup'  # a unique code

    def do(self):
        for mail in MailLog.objects.filter(sent=True, date__lte=get_today()-timedelta(days=60)):
            mail.delete()
