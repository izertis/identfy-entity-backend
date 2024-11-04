from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from openid.models import IssuanceFlow, IssuanceInformation


def update_credential_supported():
    issuance_info = IssuanceInformation.objects.filter().first()
    if issuance_info:
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
