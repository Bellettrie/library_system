from django.core.management.base import BaseCommand

from lendings.procedures.mail_late import late_mails
from mail.models import MailLog


class Command(BaseCommand):
    help = 'send email'

    def handle(self, *args, **options):
        print("HOI")
        for mail in MailLog.objects.filter(sent=False):
            print("SEND")
            mail.send()
            return
