from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from openid.models import (
    CredentialIssuerMetadata,
    IssuanceCredentialOffer,
    VCScopeAction,
)


def update_credential_supported(entity_id: int):
    metadata = CredentialIssuerMetadata.objects.filter(issuer=entity_id).first()
    if metadata:
        vc_scopes = VCScopeAction.objects.filter(entity=entity_id)
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

        metadata.credentials_supported = credentials_supported
        metadata.save()
        offer = IssuanceCredentialOffer.objects.filter(issuer=entity_id).first()
        if offer:
            offer.credentials_supported = credentials_supported
            offer.save()


@receiver(post_save, sender=VCScopeAction)
def post_save_vc_scope_action(sender, instance: VCScopeAction, **kwargs):
    update_credential_supported(instance.entity)


@receiver(post_delete, sender=VCScopeAction)
def post_delete_vc_scope_action(sender, instance: VCScopeAction, **kwargs):
    update_credential_supported(instance.entity)
