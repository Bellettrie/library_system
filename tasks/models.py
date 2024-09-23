import json
from datetime import timedelta
from operator import truediv
from typing import Protocol, runtime_checkable

import jsonpickle

from django.db import models, transaction
from django.utils import timezone
from django.utils.timezone import now


# Create your models here.
@runtime_checkable
class RunnableTask(Protocol):
    def exec(self):
        pass

    def __init_subclass__(cls, **kwargs):
        raise TypeError


class Task(models.Model):
    task_name = models.CharField(max_length=100)
    object_as_json = models.TextField()

    # The next_datetime is used to schedule tasks in the future.
    # This is mostly used for scheduled tasks, but could also be used for firing single-fire tasks in the future
    next_datetime = models.DateTimeField(default=timezone.now)

    # The done field is used to mark single_fire tasks as being finished
    # Tasks that are done should eventually be cleaned up, which is used by the CleanupOldHandledTasks task
    done = models.BooleanField(default=False)

    # The repeats_every_minutes field is used to mark a task as recurring
    # If it's set to zero, it means the task is a single-fire task.
    repeats_every_minutes = models.IntegerField(default=0,
                                                verbose_name="frequency (in minutes) of execution of task")  # Every how many minutes?

    def __str__(self):
        return "{name}[{id}] freq: {repeats_every_minutes} handled {done}".format(id=self.id, name=self.task_name,
                                                                                  repeats_every_minutes=self.repeats_every_minutes,
                                                                                  done=self.done)

    def __init__(self, *args, task_object=None, **kwargs):
        super().__init__(*args, **kwargs)

        if task_object is not None:
            # If a class is provided, we encode the class to json and use that as the text-representation
            obj_json = jsonpickle.encode(task_object)
            obj_json_data = json.dumps(obj_json, indent=4)
            self.object_as_json = obj_json_data
            self.task_object = task_object
        else:
            if self.object_as_json == "":
                return
            # If no class is provided, we use the textual JSON to get a class.
            task_obj = jsonpickle.decode(self.object_as_json)
            self.task_object = jsonpickle.loads(task_obj)

        # If the input object is not a runnable task, then we do not want to store it in the database.
        if not isinstance(self.task_object, RunnableTask):
            raise TypeError

    def register_finished(self, current_datetime):
        if self.is_recurring():
            self.next_datetime = now() + timedelta(minutes=self.repeats_every_minutes)
            self.save(update_fields=['next_datetime'])
        else:
            self.done = True
            self.save(update_fields=['done'])

    def is_recurring(self):
        return self.repeats_every_minutes > 0

    @transaction.atomic()
    def handle(self, current_datetime):
        self.task_object.exec()
        self.register_finished(current_datetime)

    # handle_next_tasks polls the next couple of tasks that could be executed and executes them
    @staticmethod
    def handle_next_tasks(count, current_datetime=None):
        if current_datetime is None:
            current_datetime = timezone.now()
        tasks = Task.objects.filter(done=False, next_datetime__lt=current_datetime).order_by('next_datetime')[:count]
        for task in tasks:
            task.handle(current_datetime)

        return len(tasks)


class CleanupOldHandledTasks:
    def __init__(self, days):
        self.days = days

    def exec(self, current_datetime=None):
        if current_datetime is None:
            current_datetime = timezone.now()
        too_old_moment = current_datetime - timedelta(days=self.days)
        Task.objects.filter(done=True, next_datetime__lte=too_old_moment).delete()
