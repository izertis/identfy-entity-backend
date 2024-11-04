# Add this code in any Django app's admin.py
# Works for all Task Statuses; you can filter them in line 12.

from django.contrib import admin
from django.contrib import messages

from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult
from .service import push_to_queue


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = push_to_queue(queryset)
    messages.info(request, msg)


retry_celery_task_admin_action.short_description = "Retry Task"  # type: ignore


class CustomTaskResultAdmin(TaskResultAdmin):
    actions = [retry_celery_task_admin_action]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)
