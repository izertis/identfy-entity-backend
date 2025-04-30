import jwt
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver

from credentials.models import VerifiableCredential
from credentials.utils import get_first_matching_element
from ebsi.enums import AccreditationTypes
from ebsi.models import PotentialAccreditationInformation


@receiver(post_delete, sender=VerifiableCredential)
def post_delete_verifiable_credential(sender, instance: VerifiableCredential, **kwargs):
    jwt_decoded = jwt.api_jwt.decode_complete(
        instance.credential,
        "",
        algorithms=["ES256", "ES256K"],
        options={"verify_signature": False},
    )
    payload = jwt_decoded.get("payload")
    vc = payload.get("vc")
    types = vc.get("type")
    accreditation_type = get_first_matching_element(AccreditationTypes.values(), types)
    if accreditation_type is None:
        return
    credential_subject = vc.get("credentialSubject")
    attribute_id = credential_subject.get("reservedAttributeId")
    items = PotentialAccreditationInformation.objects.filter(attribute_id=attribute_id)
    items.delete()


@receiver(pre_delete, sender=PotentialAccreditationInformation)
def pre_delete_potential_accreditation(sender, instance, **kwargs):
    white_lists = instance.white_lists.all()
    for list in white_lists:
        list.delete()
