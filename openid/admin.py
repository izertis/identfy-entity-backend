import uuid

from django.contrib import admin

from project import settings

from .models import (
    CredentialIssuerMetadata,
    IssuanceCredentialOffer,
    NonceManager,
    PresentationDefinition,
    VCScopeAction,
    VerifierMetadata,
    VPScopeAction,
)


# Register your models here.
class CredentialIssuerMetadataAdmin(admin.ModelAdmin):
    model = CredentialIssuerMetadata
    readonly_fields = ("credentials_supported", "issuer")

    def save_model(self, request, obj, form, change):
        obj.authorization_server = (
            obj.authorization_server or settings.BACKEND_DOMAIN
        )
        obj.credential_issuer = obj.credential_issuer or settings.BACKEND_DOMAIN
        obj.credential_endpoint = (
            obj.credential_endpoint or settings.BACKEND_DOMAIN + "/credentials/"
        )
        obj.deferred_credential_endpoint = (
            obj.deferred_credential_endpoint
            or settings.BACKEND_DOMAIN + "/credential_deferred/"
        )

        vc_scopes = VCScopeAction.objects.filter(entity=obj.issuer)
        credentials_supported = []
        for vc_scope in vc_scopes:
            credential_type = {
                "types": [
                    "VerifiableAttestation",
                    "VerifiableCredential",
                    vc_scope.credential_types,
                ],
                "format": "jwt_vc",  # Only support this format
            }
            credentials_supported.append(credential_type)

        obj.credentials_supported = credentials_supported

        super().save_model(request, obj, form, change)


class IssuanceCredentialOfferAdmin(admin.ModelAdmin):
    model = IssuanceCredentialOffer
    readonly_fields = (
        "qr",
        "credentials_supported",
        "credential_offer",
        "timestamp",
        "issuer",
    )
    date_hierarchy = "timestamp"

    def save_model(self, request, obj, form, change):
        query = CredentialIssuerMetadata.objects.filter(
            issuer=obj.issuer
        ).first()
        obj.credentials_supported = query.credentials_supported
        params = {
            "credential_issuer": settings.BACKEND_DOMAIN,
            "credentials": obj.credentials_supported,
        }
        obj.credential_offer = params
        obj.qr = settings.BACKEND_DOMAIN + "/credential-offer/qr"
        super().save_model(request, obj, form, change)


class PresentationDefinitionAdmin(admin.ModelAdmin):
    model = PresentationDefinition

    def save_model(self, request, obj, form, change):
        obj.id = obj.id or uuid.uuid4()

        super().save_model(request, obj, form, change)


class VerfierMetadataAdmin(admin.ModelAdmin):
    model = VerifierMetadata
    readonly_fields = ("scope", "verifier")

    def save_model(self, request, obj, form, change):
        obj.authorization_server = (
            obj.authorization_server
            or settings.BACKEND_DOMAIN + "/" + str(obj.issuer)
        )
        query = PresentationDefinition.objects.filter(
            id=obj.presentation_definition_id
        ).first()
        obj.scope = query.scope
        super().save_model(request, obj, form, change)


class NonceManagerAdmin(admin.ModelAdmin):
    model = NonceManager
    list_display = (
        "nonce",
        "state",
        "did",
    )


class VCScopeActionAdmin(admin.ModelAdmin):
    model = VCScopeAction
    list_display = (
        "scope",
        "response_type",
        "is_deferred",
        "credential_types",
        "entity",
    )

    readonly_fields = ("entity",)


class VPScopeActionAdmin(admin.ModelAdmin):
    model = VPScopeAction
    list_display = (
        "scope",
        "response_type",
        "presentation_definition",
        "entity",
    )
    readonly_fields = ("entity",)


admin.site.register(CredentialIssuerMetadata, CredentialIssuerMetadataAdmin)
admin.site.register(IssuanceCredentialOffer, IssuanceCredentialOfferAdmin)
admin.site.register(PresentationDefinition, PresentationDefinitionAdmin)
admin.site.register(VerifierMetadata, VerfierMetadataAdmin)
admin.site.register(NonceManager, NonceManagerAdmin)
admin.site.register(VCScopeAction, VCScopeActionAdmin)
admin.site.register(VPScopeAction, VPScopeActionAdmin)
