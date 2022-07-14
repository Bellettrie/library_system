from django_cron import CronJobBase, Schedule

from lendings.procedures.mail_late import late_mails


class LateMails(CronJobBase):
    RUN_EVERY_MINS = 120  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'lendings.send_late_mails'  # a unique code

    def do(self):
        late_mails()
