import waffle
from django.contrib import admin

from credentials.models import IssuedVerifiableCredential

from .enums import CredentialSwitches


class IssuedVerifiableCredentialAdmin(admin.ModelAdmin):
    model = (IssuedVerifiableCredential,)
    readonly_fields = (
        "vc_id",
        "vc_type",
        "hash",
        "issuance_date",
        "revocation_type",
        "revocation_info",
    )
    list_display = ("vc_id", "vc_type", "status", "issuance_date")
    list_filter = ["vc_type", "status"]
    date_hierarchy = "issuance_date"
    search_fields = ["vc_id", "vc_type"]

    def get_model_perms(self, request):
        if not waffle.switch_is_active(CredentialSwitches.CredentialStatus.value):
            return {}

        return super(IssuedVerifiableCredentialAdmin, self).get_model_perms(request)


admin.site.register(IssuedVerifiableCredential, IssuedVerifiableCredentialAdmin)
