import json
import uuid

import waffle
from django.contrib import admin
from django.db.models import JSONField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from project import settings

from .enums import OpenidSwitches
from .models import (
    IssuanceFlow,
    IssuanceInformation,
    PresentationDefinition,
    VerifyFlow,
)


# Register your models here.
class IssuanceInformationAdmin(admin.ModelAdmin):
    model = IssuanceInformation
    fields = (
        "credential_issuer_metadata_prettified",
        "qr_image",
        "url_link",
        "timestamp",
    )
    readonly_fields = (
        "credential_issuer_metadata_prettified",
        "qr_image",
        "url_link",
        "timestamp",
    )
    list_display = ("timestamp",)
    list_filter = ["credential_issuer_metadata"]

    def save_model(self, request, obj, form, change):
        obj.credential_issuer_metadata = {
            "authorization_server": f"{settings.BACKEND_DOMAIN}",
            "credential_issuer": f"{settings.BACKEND_DOMAIN}",
            "credential_endpoint": f"{settings.BACKEND_DOMAIN}/credentials/",
            "deferred_credential_endpoint": f"{settings.BACKEND_DOMAIN}/credential_deferred/",
        }
        issuance_flows = IssuanceFlow.objects.all()
        credentials_supported = []
        for issuance_flow in issuance_flows:
            credential_type = {
                "types": [
                    "VerifiableAttestation",
                    "VerifiableCredential",
                    issuance_flow.credential_types,
                ],
                "format": "jwt_vc",  # Only support this format
            }
            credentials_supported.append(credential_type)

        obj.credential_issuer_metadata["credentials_supported"] = credentials_supported

        super().save_model(request, obj, form, change)

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OpenidSwitches.OpenidSwitch.value):
            return {}

        return super(IssuanceInformationAdmin, self).get_model_perms(request)

    # Show Pretty Metadata
    def credential_issuer_metadata_prettified(self, instance):
        if instance.credential_issuer_metadata:
            """Function to display pretty version of our data"""

            # Convert the data to sorted, indented JSON
            response = json.dumps(
                instance.credential_issuer_metadata, sort_keys=True, indent=2
            )

            # Truncate the data. Alter as needed
            response = response[:5000]

            # Get the Pygments formatter
            formatter = HtmlFormatter(style="colorful")

            # Highlight the data
            response = highlight(response, JsonLexer(), formatter)

            # Get the stylesheet
            style = "<style>" + formatter.get_style_defs() + "</style><br>"

            # Safe the output
            return mark_safe(style + response)

    credential_issuer_metadata_prettified.short_description = _(
        "Credential Issuer Metadata"
    )

    # Show url to Same Device Flow
    def url_link(self, instance):
        url = f"{settings.BACKEND_DOMAIN}/credential-offer/url"
        return mark_safe(f"<a href='{url}'>{url}</a>")

    url_link.short_description = _("URL")

    # Show qr to Cross Device Flow
    def qr_image(self, instance):
        url = f"{settings.BACKEND_DOMAIN}/credential-offer/qr"
        return mark_safe('<img src="%s" width="200" height="200" />' % (url))

    qr_image.short_description = _("QR")


class PresentationDefinitionAdmin(admin.ModelAdmin):
    model = PresentationDefinition
    list_display = ("definition_id",)

    search_fields = ["definition_id"]
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    def save_model(self, request, obj, form, change):
        obj.definition_id = obj.definition_id or uuid.uuid4()
        super().save_model(request, obj, form, change)

    def get_model_perms(self, request):
        if not waffle.switch_is_active(OpenidSwitches.OpenidSwitch.value):
            return {}

        return super(PresentationDefinitionAdmin, self).get_model_perms(request)


class IssuanceFlowAdmin(admin.ModelAdmin):
    model = IssuanceFlow
    list_display = (
        "scope",
        "response_type",
        "is_deferred",
        "credential_types",
    )
    list_filter = ["credential_types"]


class VerifyFlowAdmin(admin.ModelAdmin):
    model = VerifyFlow
    readonly_fields = ("id",)
    list_display = (
        "scope",
        "response_type",
        "presentation_definition",
    )
    list_filter = ["response_type"]


admin.site.register(IssuanceInformation, IssuanceInformationAdmin)
admin.site.register(PresentationDefinition, PresentationDefinitionAdmin)
admin.site.register(IssuanceFlow, IssuanceFlowAdmin)
admin.site.register(VerifyFlow, VerifyFlowAdmin)
