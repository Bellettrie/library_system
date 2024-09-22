import json
import time
from json import JSONEncoder

import jsonpickle
from django.core.management import BaseCommand
from django.utils.timezone import now

from mail.models import MailLog, mail_member
from members.models import Member
from tasks.models import Task


class Command(BaseCommand):
    help = 'do task'

    def handle(self, *args, **options):
            for i in range(10):
                member = Member.objects.all().first()
                mail_member('mails/late_mail.tpl',
                            {'member': member, 'has_late': True,
                             'has_nearly_late': True, 'lendings': [],
                             'almost_late': []}, member, True)


            while True:
                t = Task.objects.filter(handled=False, next_datetime__lt=now())[:5]
                print("handling tasks", len(t))
                for tt in t:
                        tt.handle()
                time.sleep(10)