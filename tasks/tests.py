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

        c = Task.handle_next_tasks(1)
        self.assertEqual(c, 1)

        t_res = Task.objects.filter(task_name="fake_task").first()
        self.assertEqual(FakeTask.executed, 1)
        self.assertEqual(t_res.done, True)

        Task.objects.create(task_name="fake_task", task_object=t)
        c = Task.handle_next_tasks(1)
        self.assertEqual(c, 1)
        self.assertEqual(FakeTask.executed, 2)

    def test_picking_up_multiple_single_shot_tasks(self):
        # In this task we schedule three tasks, and handle them two per round
        # This means that we expect the first round to execute two tasks, and the second one only one
        t = FakeTask()
        Task.objects.create(task_name="fake_task", task_object=t)
        Task.objects.create(task_name="fake_task", task_object=t)
        Task.objects.create(task_name="fake_task", task_object=t)
        c = Task.handle_next_tasks(2)
        self.assertEqual(c, 2)
        self.assertEqual(FakeTask.executed, 2)

        c = Task.handle_next_tasks(2)
        self.assertEqual(c, 1)
        self.assertEqual(FakeTask.executed, 3)


    def test_done_tasks_are_not_done_again(self):
        t = FakeTask()
        Task.objects.create(task_name="fake_task", task_object=t, done=True)
        c = Task.handle_next_tasks(1)

        self.assertEqual(c, 0)
        self.assertEqual(FakeTask.executed, 0)

    def test_picks_up_recurring_task(self):
        t = FakeTask()
        tt = Task.objects.create(task_name="fake_task", task_object=t, repeats_every_minutes=1)

        c = Task.handle_next_tasks(1)
        self.assertEqual(FakeTask.executed, 1)
        self.assertEqual(c, 1)

        t_res = Task.objects.filter(task_name="fake_task").first()
        self.assertLess(tt.next_datetime, t_res.next_datetime)
        self.assertAlmostEqual(tt.next_datetime, t_res.next_datetime, delta=timedelta(minutes=1, seconds=1))


    def test_skips_recurring_task_in_future(self):
        t = FakeTask()
        Task.objects.create(task_name="fake_task", task_object=t, repeats_every_minutes=1)

        c = Task.handle_next_tasks(1, current_datetime=timezone.now() - timedelta(minutes=1))
        self.assertEqual(c, 0)
        self.assertEqual(FakeTask.executed, 0)
