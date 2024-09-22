import json
from datetime import timedelta
from operator import truediv
from typing import Protocol, runtime_checkable

import jsonpickle

from django.db import models, transaction
from django.utils.timezone import now


# Create your models here.
@runtime_checkable
class RunnableTask(Protocol):
    def exec(self): ...

    def __init_subclass__(cls, **kwargs):
        raise TypeError


class Task(models.Model):
    task_name = models.CharField(max_length=100)
    object_as_json = models.TextField()

    handled = models.BooleanField(default=False)
    next_datetime = models.DateTimeField(auto_now_add=True)
    every = models.IntegerField(default=0,
                                verbose_name="frequency (in minutes) of execution of task")  # Every how many minutes?

    def __str__(self):
        return "{name}[{id}] freq: {every} handled {handled}".format(id=self.id, name=self.task_name,
                                                                     every=self.every, handled=self.handled)

    def __init__(self, *args, task_object=None, **kwargs):
        super().__init__(*args, **kwargs)
        if task_object is not None:
            obj_json = jsonpickle.encode(task_object)
            obj_json_data = json.dumps(obj_json, indent=4)
            self.object_as_json = obj_json_data
            self.task_object = task_object
        else:
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
