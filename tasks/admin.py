from django.contrib import admin

from tasks.models import Task


# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    class Meta:
        model = Task

    ordering = ('-next_datetime',)
    list_display = ('id', 'task_name', 'repeats_every_minutes', 'next_datetime', 'done')
    list_filter = ('task_name', 'done')


admin.site.register(Task, TaskAdmin)
