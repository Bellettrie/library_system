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

    handled = models.BooleanField(default=False)
    next_datetime = models.DateTimeField(default=timezone.now)
    every = models.IntegerField(default=0,
                                verbose_name="frequency (in minutes) of execution of task")  # Every how many minutes?

    def __str__(self):
        return "{name}[{id}] freq: {every} handled {handled}".format(id=self.id, name=self.task_name,
                                                                     every=self.every, handled=self.handled)

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

        if not isinstance(self.task_object, RunnableTask):
            raise TypeError

    def register_finished(self):
        if self.is_recurring():
            self.next_datetime = now() + timedelta(minutes=self.every)
        else:
            self.handled = True
        self.save()

    def is_recurring(self):
        return self.every > 0

    @transaction.atomic()
    def handle(self):
        self.task_object.exec()
        self.register_finished()


class CleanupOldHandledTasks:
    def __init__(self, days):
        self.days = days

    def exec(self):
        too_old_moment = now() - timedelta(days=self.days)
        Task.objects.filter(handled=True, next_datetime__lte=too_old_moment).delete()
