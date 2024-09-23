import json
import time
from json import JSONEncoder

import jsonpickle
from django.core.management import BaseCommand
from django.utils.timezone import now

from mail.models import MailLog, mail_member
from members.models import Member
from tasks.models import Task
from django.conf import settings


class Command(BaseCommand):
    help = 'do task'

    def handle(self, *args, **options):
        print("Polling every ", settings.TASK_POLL_FREQUENCY)
        while True:
            Task.handle_next_tasks(5)
            time.sleep(settings.TASK_POLL_FREQUENCY)
