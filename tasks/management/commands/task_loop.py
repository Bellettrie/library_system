import logging
import time

from django.core.management import BaseCommand

from tasks.models import Task
from django.conf import settings


class Command(BaseCommand):
    help = 'do task'

    def handle(self, *args, **options):
        print("Polling every ", settings.TASK_POLL_FREQUENCY)
        while True:
            handled = Task.handle_next_tasks(5)
            if handled > 0:
                logging.info("handled tasks", handled)

            time.sleep(settings.TASK_POLL_FREQUENCY)
