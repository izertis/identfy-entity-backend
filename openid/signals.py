from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ebsi.enums import AccreditationTypes
from ebsi.models import EbsiAccreditation
from openid.models import IssuanceFlow, IssuanceInformation


def update_credential_supported():
    issuance_info = IssuanceInformation.objects.first()
    if issuance_info is None:
        return
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
    if issuance_info.include_ebsi_accreditations:
        accreditations = EbsiAccreditation.objects.all()
        for accreditation in accreditations:
            types = [
                "VerifiableAttestation",
                "VerifiableCredential",
                accreditation.type,
            ]
            if (
                accreditation.type
                != AccreditationTypes.VerifiableAuthorisationToOnboard.value
            ):
                types.insert(0, "VerifiableAccreditation")
            credentials_supported.append(
                {
                    "types": types,
                    "format": "jwt_vc",
                }
            )
    issuance_info.credential_issuer_metadata["credentials_supported"] = (
        credentials_supported
    )
    issuance_info.save()


@receiver(post_save, sender=IssuanceFlow)
def post_save_issuance_flow(sender, instance: IssuanceFlow, **kwargs):
    update_credential_supported()


@receiver(post_delete, sender=IssuanceFlow)
def post_delete_issuance_flow(sender, instance: IssuanceFlow, **kwargs):
    update_credential_supported()


@receiver(post_delete, sender=EbsiAccreditation)
def post_delete_ebsi_accreditation(sender, instance: EbsiAccreditation, **kwargs):
    update_credential_supported()
