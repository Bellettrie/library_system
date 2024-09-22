from datetime import timedelta

from django_cron import CronJobBase, Schedule

from mail.models import MailLog
from utils.time import get_today


class SendSingleEmail(CronJobBase):
    def exec(self):
        for mail in MailLog.objects.filter(sent=False):
            mail.send()
            return


class CleanMailLog(CronJobBase):
    def exec(self):
        for mail in MailLog.objects.filter(sent=True, date__lte=get_today() - timedelta(days=60)):
            mail.delete()
