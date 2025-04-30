import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from openid.enums import RevocationTypes, ScopeResponseType


# Create your models here.
class IssuanceInformation(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
    include_ebsi_accreditations = models.BooleanField(
        default=False, verbose_name="Include EBSI accreditations"
    )
    credential_issuer_metadata = models.JSONField(
        _("Credential Issuer Metadata"),
        max_length=22500,
        null=False,
        blank=True,
        default=dict,
    )

    timestamp = models.DateTimeField(_("Timestamp"), auto_now=True)

    class Meta:
        verbose_name = "Issuance Information"
        verbose_name_plural = "Issuance Information"

    def clean(self):
        from ebsi.models import EbsiAccreditation

        search = IssuanceFlow.objects.all().exists()
        accreditation_search = EbsiAccreditation.objects.all().exists()
        if not search and not accreditation_search:
            raise ValidationError(
                _(
                    "You need to add Issuance Flow first or have the right to emit an accreditation"
                )
            )


class PresentationDefinition(models.Model):
    definition_id = models.CharField(_("Identifier"), max_length=2500, blank=True)
    format = models.JSONField(_("Format"), blank=True)
    descriptors = models.JSONField(_("Input Descriptors"))

    class Meta:
        verbose_name = "Presentation Definition"
        verbose_name_plural = "Presentation Definitions"
        constraints = [
            models.UniqueConstraint(
                fields=["definition_id"],
                name="Definition ID already exists",
            )
        ]

    def clean(self):
        if isinstance(self.descriptors, list):
            for descriptor in self.descriptors:
                if not isinstance(descriptor, dict):
                    raise ValidationError(
                        _(
                            "Each elemento of the input descriptor array must be an object"
                        )
                    )
        else:
            raise ValidationError(
                _("The inputs descriptors field must be an array of objects")
            )

    def __str__(self) -> str:
        return f"{self.definition_id}"


class NonceManager(models.Model):
    nonce = models.CharField(_("Nonce"), max_length=2000, primary_key=True)
    state = models.JSONField(_("State"), null=True, blank=True)

    class Meta:
        verbose_name = "Nonce Manager"
        verbose_name_plural = "Nonces Manager"

    def __str__(self) -> str:
        return f"{self.nonce}"


class IssuanceFlow(models.Model):
    scope = models.CharField(_("Scope"), max_length=2000, null=False, default="openid")
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
    revocation = models.CharField(
        _("Type of revocation on EBSI"),
        default=RevocationTypes.status_list_2021,
        choices=RevocationTypes.choices(),
        max_length=100,
        null=True,
        blank=True,
    )
    expires_in = models.IntegerField(
        _("Expires in (s)"),
        validators=[
            MinValueValidator(0),
        ],
        null=True,
        blank=True,
    )

    terms_of_use = models.ForeignKey(
        "ebsi.EbsiTermsOfUse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Issuance Flow"
        verbose_name_plural = "Issuance Flows"

    def clean(self):
        search = IssuanceFlow.objects.filter(
            credential_types=self.credential_types
        ).first()
        if search and (self.id is None):
            raise ValidationError(_("This Credential Type alredy exists"))
        if self.response_type == ScopeResponseType.vp_token and (
            self.presentation_definition is None
        ):
            raise ValidationError(
                _(
                    "If you want to use vp_token, you must define a Presentation definition"
                )
            )
        if (
            self.response_type == ScopeResponseType.id_token
            and self.presentation_definition
        ):
            raise ValidationError(
                _("Id_token response type doesn't use Presentation definition")
            )
        if self.terms_of_use is not None:
            self.check_terms_of_use()
        if self.revocation == RevocationTypes.status_list_2021.name:
            self.check_ebsi_proxy_api()

    def check_terms_of_use(self):
        if self.credential_types not in self.terms_of_use.type:
            raise ValidationError(
                _("The selected Terms of Use is not valid for the specified VC Type")
            )
        if self.credential_schema_address != self.terms_of_use.vc_schema:
            raise ValidationError(
                _(
                    "The selected schema address is not valid for the specified Terms of Use"
                )
            )

    def check_ebsi_proxy_api(self):
        from ebsi.models import ProxyAPIs

        if ProxyAPIs.objects.all().first() is None:
            raise ValidationError(
                _(
                    "To use this revocation method in the EBSI network first a proxy API must be registered"
                )
            )

    def __str__(self) -> str:
        return f"{self.scope}"


class VerifyFlow(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=36
    )
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

    class Meta:
        verbose_name = "Verify Flow"
        verbose_name_plural = "Verify Flows"
        constraints = [
            models.UniqueConstraint(
                fields=["scope"], name="This Scope is alredy defined"
            )
        ]

    def __str__(self) -> str:
        return f"{self.scope}"
