import re

from django.db.models.signals import post_save
from django.dispatch import receiver

from common.constants.ebsi_constants import EBSI_RESERVED_TYPES
from credentials.models import IssuedVerifiableCredential
from ebsi.models import PotentialAccreditationInformation
from ebsi.service import EbsiService


@receiver(post_save, sender=IssuedVerifiableCredential)
def post_save_issued_vc(sender, instance: IssuedVerifiableCredential, **kwargs):
    if instance.revocation_type == "EbsiAccreditationEntry":
        vc_type = [
            element
            for element in instance.vc_type
            if element not in EBSI_RESERVED_TYPES
        ][0]
        potential_accreditation_list = PotentialAccreditationInformation.objects.filter(
            type=vc_type
        ).first()
        if potential_accreditation_list is None:
            raise Exception("No accreditation attributes available")

        attribute = potential_accreditation_list.attribute_id
        id = instance.revocation_info.get("id")
        revision_id = re.search(r"0x[0-9a-fA-F]+", id).group()

        EbsiService.revoke_accreditation(instance.holder, attribute, revision_id)
