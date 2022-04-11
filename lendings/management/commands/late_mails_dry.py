from django.core.management.base import BaseCommand

from lendings.procedures.mail_late import late_mails


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        mails = late_mails(fake=True)
        print(mails)
