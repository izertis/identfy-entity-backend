import math
from operator import itemgetter

import jwt
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from credentials.utils import get_first_matching_element
from ebsi.enums import AccreditationTypes
from ebsi.models import (
    EbsiAccreditation,
    EbsiTermsOfUse,
    PotentialAccreditationInformation,
)
from ebsi.tasks import onboard_ebsi_entity, register_trusted_entity_and_proxy_api
from project import settings


# Create your models here.
class VerifiableCredential(models.Model):
    credential = models.CharField(
        _("Credential (JWT Format)"), max_length=4000, null=True, blank=True
    )

    class Meta:
        verbose_name = "Verifiable Credential"
        verbose_name_plural = "Verifiable Credentials"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        jwt_decoded = jwt.api_jwt.decode_complete(
            self.credential,
            "",
            algorithms=["ES256", "ES256K"],
            options={"verify_signature": False},
        )
        payload = jwt_decoded.get("payload")

        vc = payload.get("vc")

        credential_subject = vc.get("credentialSubject")
        if self.check_if_accreditation_already_exists(
            credential_subject.get("reservedAttributeId"),
        ):
            return

        types = vc.get("type")

        holder_did = credential_subject.get("id")

        accreditation_type = get_first_matching_element(
            AccreditationTypes.values(), types
        )

        accredited_for_array = credential_subject.get("accreditedFor")
        attribute_id = credential_subject.get("reservedAttributeId")
        if attribute_id is None:
            attribute_id = vc.get("reservedAttributeId")
        if (
            accreditation_type is not None
            and holder_did is not None
            and holder_did == settings.DID
        ):
            if (
                accreditation_type
                == AccreditationTypes.VerifiableAccreditationForTrustChain
                or accreditation_type
                == AccreditationTypes.VerifiableAccreditationToAccredit
            ):
                self.create_accreditation_instance(
                    AccreditationTypes.VerifiableAccreditationToAccredit.value,
                )
                self.create_accreditation_instance(
                    AccreditationTypes.VerifiableAccreditationToAttest.value,
                )
                self.create_accreditation_instance(
                    AccreditationTypes.VerifiableAuthorisationToOnboard.value,
                )
                (
                    all_potential_accreditation_info,
                    all_terms_of_use,
                ) = itemgetter("all_potential_accreditation_info", "all_terms_of_use")(
                    self.fill_accreditation_info_and_terms_of_use(
                        accredited_for_array, attribute_id
                    )
                )
                all_potential_accreditation_info.append(
                    PotentialAccreditationInformation(
                        type=AccreditationTypes.VerifiableAuthorisationToOnboard.value,
                        accredited_for=[],
                        attribute_id=attribute_id,
                    )
                )
                PotentialAccreditationInformation.objects.bulk_create(
                    all_potential_accreditation_info
                )
                EbsiTermsOfUse.objects.bulk_create(all_terms_of_use)
                register_trusted_entity_and_proxy_api.delay(self.credential)
                # TODO: Register VC in EBSI Ecosystem
            if (
                accreditation_type
                == AccreditationTypes.VerifiableAccreditationToAttest.value
            ):
                # Create accreditation instance for VerifiableAuthorisationToOnboard
                self.create_accreditation_instance(
                    AccreditationTypes.VerifiableAuthorisationToOnboard.value,
                )
                PotentialAccreditationInformation(
                    type=AccreditationTypes.VerifiableAuthorisationToOnboard.value,
                    accredited_for=[],
                    attribute_id=attribute_id,
                ).save()
                all_terms_of_use = []
                for value in accredited_for_array:
                    all_terms_of_use.append(
                        self.create_terms_of_use_instance(
                            attribute_id,
                            value.get("types"),
                            value.get("schemaId"),
                        )
                    )
                EbsiTermsOfUse.objects.bulk_create(all_terms_of_use)
                register_trusted_entity_and_proxy_api.delay(self.credential)
                # TODO: Register VC in EBSI Ecosystem
            if (
                accreditation_type
                == AccreditationTypes.VerifiableAuthorisationToOnboard
            ):
                onboard_ebsi_entity.delay(self.credential)

    def fill_accreditation_info_and_terms_of_use(
        self, accredited_for_array, attribute_id
    ) -> dict:
        all_potential_accreditation_info = []
        all_terms_of_use = []
        if accredited_for_array is not None and len(accredited_for_array) > 0:
            for value in accredited_for_array:
                all_terms_of_use.append(
                    self.create_terms_of_use_instance(
                        attribute_id,
                        value.get("types"),
                        value.get("schemaId"),
                    )
                )
                all_potential_accreditation_info.extend(
                    [
                        PotentialAccreditationInformation(
                            type=AccreditationTypes.VerifiableAccreditationToAccredit.value,
                            accredited_for=value.get("types"),
                            accredited_schema=value.get("schemaId"),
                            attribute_id=attribute_id,
                        ),
                        PotentialAccreditationInformation(
                            type=AccreditationTypes.VerifiableAccreditationToAttest.value,
                            accredited_for=value.get("types"),
                            accredited_schema=value.get("schemaId"),
                            attribute_id=attribute_id,
                        ),
                    ]
                )
        else:
            all_terms_of_use.append(
                self.create_terms_of_use_instance(
                    attribute_id,
                    [],
                    None,
                )
            )
            all_potential_accreditation_info.extend(
                [
                    PotentialAccreditationInformation(
                        type=AccreditationTypes.VerifiableAccreditationToAccredit.value,
                        accredited_for=[],
                        accredited_schema=None,
                        attribute_id=attribute_id,
                    ),
                    PotentialAccreditationInformation(
                        type=AccreditationTypes.VerifiableAccreditationToAttest.value,
                        accredited_for=[],
                        accredited_schema=None,
                        attribute_id=attribute_id,
                    ),
                ]
            )
        return {
            "all_potential_accreditation_info": all_potential_accreditation_info,
            "all_terms_of_use": all_terms_of_use,
        }

    def check_if_accreditation_already_exists(self, attribute_id):
        return (
            PotentialAccreditationInformation.objects.filter(
                attribute_id=attribute_id,
            ).first()
            is not None
        )

    def create_accreditation_instance(self, type):
        if EbsiAccreditation.objects.filter(type=type).first() is None:
            EbsiAccreditation(type=type).save()

    def create_terms_of_use_instance(
        self, attribute_id, type, schema
    ) -> EbsiTermsOfUse:
        return EbsiTermsOfUse(
            type=type,
            attribute_id=attribute_id,
            vc=self,
            vc_schema=schema,
        )


class StatusList2021(models.Model):
    content = models.BinaryField()
    current_index = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(131071),  # 16 * 1024 * 8 - 1
        ],
        null=True,
    )

    class Meta:
        verbose_name = "StatusList2021"
        verbose_name_plural = "StatusLists2021"

    def __str__(self) -> str:
        return f"{self.id}"

    def save(self, *args, **kwargs):
        if not self.content:
            self.content = bytearray(16 * 1024)
        return super().save(*args, **kwargs)


class IssuedVerifiableCredential(models.Model):
    vc_id = models.CharField(
        _("VC Identifier"), max_length=4000, null=False, primary_key=True
    )
    vc_type = ArrayField(models.CharField(max_length=4000), verbose_name=_("VC Types"))
    hash = models.CharField(
        _("Credential hash"), max_length=4000, null=True, blank=True
    )
    issuance_date = models.DateTimeField(_("Issuance Date"), null=False)
    status = models.BooleanField(_("Revocation status"), default=False)
    revocation_type = models.CharField(
        _("Revocation Type"), max_length=4000, null=True, blank=True
    )
    revocation_info = models.JSONField(
        _("Revocation Information"), null=True, blank=True
    )
    holder = models.CharField(_("Holder DID"), max_length=4000, null=False)

    def clean(self):
        if not self.status:
            # Check if the data was set to true before
            current_model = IssuedVerifiableCredential.objects.filter(
                vc_id=self.vc_id
            ).last()
            if current_model.status:
                raise ValidationError("Can't restore the status of a revoked VC")

    def save(self, *args, **kwargs):
        if self.status and self.revocation_type == "StatusList2021Entry":
            revocation_info = self.revocation_info
            list_array = revocation_info["statusListCredential"].split("/")
            status_list_id = list_array[len(list_array) - 1]
            index = int(revocation_info["statusListIndex"])
            status_list = StatusList2021.objects.filter(id=status_list_id).last()
            byte_index = math.floor(index / 8)
            bit_index = int(index) % 8
            list_data = bytearray(status_list.content)
            list_data[byte_index] |= 128 >> bit_index
            status_list.content = list_data
            status_list.save()

        return super().save(*args, **kwargs)
