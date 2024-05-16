from django.core.management.base import BaseCommand
from lendings.procedures.mail_late import late_mails


class Command(BaseCommand):
    help = 'Send late mails'

    def handle(self, *args, **options):
        late_mails()
