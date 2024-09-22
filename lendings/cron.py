from django_cron import CronJobBase, Schedule

from lendings.procedures.mail_late import late_mails


class LateMails:
    def exec(self):
        late_mails()
