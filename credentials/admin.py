import json

import jwt
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from credentials.models import IssuedVerifiableCredential, VerifiableCredential
from project.settings import BACKEND_DOMAIN


class VerifiableCredentialAdmin(admin.ModelAdmin):
    model = VerifiableCredential
    readonly_fields = ("credential_prettified", "vc_types")
    list_display = ("vc_types",)
    search_fields = ["vc_types"]

    def credential_prettified(self, instance):
        if instance.credential:
            """Function to display pretty version of our data"""
            jwt_decoded = jwt.api_jwt.decode_complete(
                instance.credential,
                "",
                algorithms=None,
                options={"verify_signature": False},
            )
            headers_payload = {
                "header": jwt_decoded.get("header"),
                "payload": jwt_decoded.get("payload"),
            }
            # Convert the data to sorted, indented JSON
            response = json.dumps(headers_payload, sort_keys=True, indent=2)

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

    credential_prettified.short_description = _("Credential (JSON Format)")

    def vc_types(self, instance):
        if instance.credential:
            """Function to display pretty version of our data"""
            jwt_decoded = jwt.api_jwt.decode_complete(
                instance.credential,
                "",
                algorithms=["ES256", "ES256K"],
                options={"verify_signature": False},
            )
            payload = jwt_decoded.get("payload")

            # Convert the data to sorted, indented JSON
            response = json.dumps(
                payload.get("vc").get("type"), sort_keys=True, indent=2
            )

            # Safe the output
            return response

    vc_types.short_description = _("Credential Type")


class IssuedVerifiableCredentialAdmin(admin.ModelAdmin):
    model = (IssuedVerifiableCredential,)
    readonly_fields = (
        "vc_id",
        "vc_type",
        "hash",
        "issuance_date",
        "revocation_type",
        "revocation_info",
        "holder",
    )
    list_display = ("vc_id", "vc_type", "status", "issuance_date", "holder")
    list_filter = ["vc_type", "status", "holder"]
    date_hierarchy = "issuance_date"
    search_fields = ["vc_id", "vc_type", "holder"]


admin.site.register(VerifiableCredential, VerifiableCredentialAdmin)
admin.site.register(IssuedVerifiableCredential, IssuedVerifiableCredentialAdmin)


def request_vc_from_external_issuer(request):
    context = admin.site.each_context(request)
    # TODO: ENTITIES NO EXISTE AHORA
    context["backend"] = BACKEND_DOMAIN
    return TemplateResponse(request, "request_vc/request_vc.html", context)
