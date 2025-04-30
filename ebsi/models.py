from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from ebsi.constants import EBSI_ACCREDITATION_REVOCATION_TYPE, EBSI_ATTESTATION_SCHEMA
from ebsi.enums import AccreditationTypes
from openid.enums import ScopeResponseType
from openid.models import IssuanceFlow, PresentationDefinition


class EbsiTermsOfUse(models.Model):
    type = ArrayField(
        models.CharField(
            max_length=100,
        ),
        verbose_name=_("VC Type"),
    )
    vc_schema = models.CharField(max_length=1000, null=True)
    attribute_id = models.CharField(_("Attribute ID"), max_length=4000, null=True)
    vc = models.ForeignKey(
        "credentials.VerifiableCredential", on_delete=models.CASCADE, null=False
    )

    def __str__(self):
        return f"{self.attribute_id}"


# Create your models here.
class EbsiAccreditation(models.Model):
    type = models.CharField(
        _("Accreditation Type"),
        choices=AccreditationTypes.choices(),
        max_length=100,
        null=False,
        blank=False,
    )
    token = models.CharField(
        _("Response Type"),
        default=ScopeResponseType.id_token.name,
        choices=ScopeResponseType.choices(),
        max_length=100,
        null=False,
        blank=False,
    )
    presentation_definition = models.ForeignKey(
        PresentationDefinition, on_delete=models.SET_NULL, null=True, blank=True
    )

    def to_scope_action(self):
        return IssuanceFlow(
            response_type=self.token,
            is_deferred=False,
            # TODO: In the future, we will probably have to use (EBSI Verifiable Accreditation Record) https://api-pilot.ebsi.eu/trusted-schemas-registry/v2/schemas/zG6xY9DG2CWyhsSc544hEezbQRmkQCfvgXGdCqt69v8TA
            credential_schema_address=EBSI_ATTESTATION_SCHEMA,
            presentation_definition=self.presentation_definition,
            revocation=EBSI_ACCREDITATION_REVOCATION_TYPE,
            credential_types=self.type,
        )


class PotentialAccreditationInformation(models.Model):
    type = models.CharField(_("type"), max_length=2000, null=False)
    accredited_for = ArrayField(
        models.CharField(
            max_length=100,
        ),
        verbose_name=_("Accredit for type"),
    )
    accredited_schema = models.CharField(
        _("Accredited Schema"), max_length=4000, null=True
    )
    attribute_id = models.CharField(_("Attribute ID"), max_length=4000, null=True)

    def __str__(self) -> str:
        return f"{self.type}-{self.attribute_id}"

    class Meta:
        verbose_name = "Potential Accreditation information"
        verbose_name_plural = "Potential Accreditations information"


class EbsiAccreditationWhiteList(models.Model):
    type = models.CharField(_("type"), max_length=2000, null=False)
    did = models.CharField(_("DID"), max_length=2000, null=False)
    schema = models.ManyToManyField(
        PotentialAccreditationInformation, related_name="white_lists"
    )

    class Meta:
        unique_together = [["type", "did"]]


class AccreditationToAttest(EbsiAccreditationWhiteList):
    class Meta:
        proxy = True


class AccreditationToAccredit(EbsiAccreditationWhiteList):
    class Meta:
        proxy = True


class AccreditationToOnboard(EbsiAccreditationWhiteList):
    class Meta:
        proxy = True


class ProxyAPIs(models.Model):
    proxy_id = models.CharField(_("proxy_id"), max_length=64, null=False)
