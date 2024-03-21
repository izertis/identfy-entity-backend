import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from openid.enums import ScopeResponseType
from project import settings


# Create your models here.
class CredentialIssuerMetadata(models.Model):
    issuer = models.CharField(
        _("Issuer"), max_length=200, default=settings.DID, primary_key=True
    )
    authorization_server = models.CharField(
        _("Authorization Server"), max_length=200, null=True, blank=True
    )
    credential_issuer = models.CharField(
        _("Credential Issuer"), max_length=200, null=True, blank=True
    )
    credential_endpoint = models.CharField(
        _("Credential Endpoint"), max_length=200, null=True, blank=True
    )
    deferred_credential_endpoint = models.CharField(
        _("Deferred Credential Endpoint"), max_length=200, null=True, blank=True
    )
    credentials_supported = models.JSONField(_("Supported Credentials"))

    class Meta:
        verbose_name = "Credential Issuer Metadata"
        verbose_name_plural = "Credential Issuers Metadata"

    def clean(self):
        metadata = CredentialIssuerMetadata.objects.filter(issuer=self.issuer)
        if metadata:
            raise ValidationError(
                _("You already have a Credential Metadata, you can update it")
            )
        search = VCScopeAction.objects.filter(entity=self.issuer)
        if not search:
            raise ValidationError(_("You need to add VC Scope Action first"))

    def __str__(self) -> str:
        return f"{self.credential_issuer}"


class IssuanceCredentialOffer(models.Model):
    issuer = models.CharField(
        _("Issuer"), max_length=200, default=settings.DID, primary_key=True
    )
    credentials_supported = models.JSONField(_("Supported Credentials"))
    credential_offer = models.CharField(_("Credential Offer"), max_length=2500)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now=True)
    qr = models.URLField(_("QR"))

    class Meta:
        verbose_name = "Issuance Credential Offer"
        verbose_name_plural = "Issuance Credential Offers"

    def clean(self):
        offer = IssuanceCredentialOffer.objects.filter(issuer=self.issuer)
        if offer:
            raise ValidationError(
                _("You already have an Issuance Offer, you can update it")
            )
        search = CredentialIssuerMetadata.objects.filter(issuer=self.issuer)
        if not search:
            raise ValidationError(
                _("You need to add Credential Metadata first")
            )

    def __str__(self) -> str:
        return f"{self.issuer}"


class PresentationDefinition(models.Model):
    id = models.CharField(_("Identifier"), max_length=2500, primary_key=True)
    scope = models.CharField(
        _("Scope"), max_length=100, null=False, unique=True
    )
    content = models.JSONField(_("Content"), null=False)

    class Meta:
        verbose_name = "Presentation Definition"
        verbose_name_plural = "Presentation Definitions"

    def __str__(self) -> str:
        return f"{self.id}"


class VerifierMetadata(models.Model):
    verifier = models.CharField(
        _("Verifier"), max_length=200, default=settings.DID, primary_key=True
    )
    authorization_server = models.CharField(
        _("Authorization Server"), max_length=200, null=True, blank=True
    )
    presentation_definition_id = models.ForeignKey(
        PresentationDefinition, on_delete=models.CASCADE, null=False
    )
    scope = models.CharField(_("Scope"), max_length=200, null=False)

    class Meta:
        verbose_name = "Verifier Metadata"
        verbose_name_plural = "Verifiers Metadata"

    def __str__(self) -> str:
        return f"{self.authorization_server}"


class NonceManager(models.Model):
    nonce = models.CharField(_("Nonce"), max_length=2000, primary_key=True)
    state = models.JSONField(_("State"), null=True, blank=True)
    did = models.CharField(_("Did"), max_length=200, null=False, blank=False)

    class Meta:
        verbose_name = "Nonce Manager"
        verbose_name_plural = "Nonces Manager"

    def __str__(self) -> str:
        return f"{self.nonce}"


class VCScopeAction(models.Model):
    scope = models.CharField(
        _("Scope"), max_length=2000, null=False, default="openid"
    )
    response_type = models.CharField(
        _("Response Type"),
        default=ScopeResponseType.id_token.name,
        choices=ScopeResponseType.choices(),
        max_length=100,
        null=False,
        blank=False,
    )

    is_deferred = models.BooleanField(
        _("Deferred"), default=False, null=False, blank=False
    )

    credential_types = models.CharField(
        _("Credential Type"), max_length=2000, null=False
    )
    credential_schema_address = models.CharField(
        _("Credential Schema"), max_length=2000, null=False
    )
    presentation_definition = models.ForeignKey(
        PresentationDefinition, on_delete=models.SET_NULL, null=True, blank=True
    )
    entity = models.CharField(_("Entity"), default=settings.DID, max_length=200)

    class Meta:
        verbose_name = "VC Scope Action"
        verbose_name_plural = "VC Scope Actions"

    def clean(self):
        search = VCScopeAction.objects.filter(
            credential_types=self.credential_types
        ).first()
        if search and self.id == None:
            raise ValidationError(_("This Credential_types alredy exists"))
        if (
            self.response_type == ScopeResponseType.vp_token
            and self.presentation_definition == None
        ):
            raise ValidationError(
                _(
                    "If you want to use vp_token, you must define Presentation definition"
                )
            )
        if (
            self.response_type == ScopeResponseType.id_token
            and self.presentation_definition
        ):
            raise ValidationError(
                _("Id_token response type doesn't use Presentation definition")
            )

    def __str__(self) -> str:
        return f"{self.scope}"


class VPScopeAction(models.Model):
    scope = models.CharField(_("Scope"), max_length=2000, null=False)
    response_type = models.CharField(
        _("Response Type"),
        default=ScopeResponseType.vp_token.name,
        choices=ScopeResponseType.choices(),
        max_length=100,
        null=False,
        blank=False,
    )

    presentation_definition = models.ForeignKey(
        PresentationDefinition, on_delete=models.SET_NULL, null=True, blank=True
    )

    entity = models.CharField(
        _("Entity"), default=settings.DID, max_length=200, editable=False
    )

    class Meta:
        verbose_name = "VP Scope Action"
        verbose_name_plural = "VP Scope Actions"

    def clean(self):
        search = VPScopeAction.objects.filter(scope=self.scope).first()
        if search and self.id == None:
            raise ValidationError(_("This Scope alredy exists"))

    def __str__(self) -> str:
        return f"{self.scope}"
