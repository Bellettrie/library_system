from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from tasks.models import Task


# Used to verify that tasks are actually executed

class FakeTask:
    executed = 0

    def exec(self):
        FakeTask.executed += 1


class TaskTestCase(TestCase):
    def setUp(self):
        Task.objects.all().delete()

    def test_picks_up_single_shot_task(self):
        t = FakeTask()
        Task.objects.create(task_name="fake_task", task_object=t)

        Task.handle_next_tasks(1)

        t_res = Task.objects.filter(task_name="fake_task").first()
        self.assertEqual(FakeTask.executed, 1)
        self.assertEqual(t_res.done, True)

        Task.objects.create(task_name="fake_task", task_object=t)
        Task.handle_next_tasks(1)
        self.assertEqual(FakeTask.executed, 2)

    def test_picks_up_recurring_task(self):
        t = FakeTask()
        tt = Task.objects.create(task_name="fake_task", task_object=t, repeats_every_minutes=1)

        Task.handle_next_tasks(1)
        self.assertEqual(FakeTask.executed, 1)
        t_res = Task.objects.filter(task_name="fake_task").first()
        self.assertLess(tt.next_datetime, t_res.next_datetime)
        self.assertAlmostEqual(tt.next_datetime, t_res.next_datetime, delta=timedelta(minutes=1, seconds=1))


    def test_skips_recurring_task_in_future(self):
        t = FakeTask()
        Task.objects.create(task_name="fake_task", task_object=t, repeats_every_minutes=1)

        Task.handle_next_tasks(1, current_datetime=timezone.now() - timedelta(minutes=1))
        self.assertEqual(FakeTask.executed, 0)
