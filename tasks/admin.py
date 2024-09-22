from django.contrib import admin

from tasks.models import Task


# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    class Meta:
        model = Task

    ordering = ('-next_datetime',)
    list_display = ('id', 'task_name', 'every', 'next_datetime', 'handled')
    list_filter = ('task_name', 'handled')


admin.site.register(Task, TaskAdmin)
