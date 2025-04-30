from django.contrib import admin

from .models import OrganizationKeys


class OrganizationKeysAdmin(admin.ModelAdmin):
    model = OrganizationKeys
    list_filter = ["name"]
    search_fields = [
        "organization__id",
    ]
    list_display = (
        "name",
        "type",
        "format",
    )


admin.site.register(OrganizationKeys, OrganizationKeysAdmin)
