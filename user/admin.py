from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import GroupResult, TaskResult
from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework.authtoken.models import TokenProxy
from waffle.models import Flag, Sample, Switch

from user.forms import MyUserForm


class CustomUserAdmin(UserAdmin):
    add_form = MyUserForm
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    readonly_fields = ("date_joined", "last_login")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(id=request.user.id)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(ResetPasswordToken)
admin.site.unregister(Flag)
admin.site.unregister(Sample)
admin.site.unregister(Switch)
admin.site.unregister(TokenProxy)
admin.site.unregister(GroupResult)
admin.site.unregister(TaskResult)
