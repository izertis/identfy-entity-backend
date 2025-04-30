import json
from typing import List

import jwt
import requests
from django.core.exceptions import BadRequest
from django.utils.translation import gettext_lazy as _

from common.constants.ebsi_constants import EBSI_RESERVED_TYPES
from credentials.serializers import (
    CredentialResponseSerializer,
    EbsiCredentialRequestSerializer,
)
from ebsi.models import PotentialAccreditationInformation, ProxyAPIs
from openid.enums import RevocationTypes
from openid.models import IssuanceFlow
from project import settings

from .models import IssuedVerifiableCredential, StatusList2021


class CredentialStrategy:
    def __init__(self, request, token):
        self.request = request
        self.token = token

    def _ebsi_get_specific_type(types: List[str]) -> List[str]:
        return [element for element in types if element not in EBSI_RESERVED_TYPES]

    def ebsi_credentials(self) -> CredentialResponseSerializer:
        url = settings.VC_SERVICE_URL + "/credentials"
        request_post: EbsiCredentialRequestSerializer = self.request.data
        headers = {
            "Authorization": self.token,
        }

        payload = {
            "types": request_post["types"],
            "format": request_post["format"],
            "proof": request_post["proof"],
            "issuerUri": settings.BACKEND_DOMAIN,
            "issuerDid": settings.DID,
        }

        vc_specific_types = CredentialStrategy._ebsi_get_specific_type(
            request_post["types"]
        )
        if len(vc_specific_types) != 1:
            raise BadRequest(_("Invalid credential types"))

        scope_action = IssuanceFlow.objects.filter(
            credential_types=vc_specific_types[0]
        ).first()
        if scope_action:
            if scope_action.revocation == RevocationTypes.status_list_2021.name:
                proxy = ProxyAPIs.objects.first()
                if not proxy:
                    return {
                        "status_code": 500,
                        "content": "The requested VC can't be issued at this momment ",
                    }
                # Reserve index for StatusList
                next_index = None
                status_list = StatusList2021.objects.all()
                status_list = status_list.latest("id")
                if status_list.current_index == 16 * 1024 * 8 - 1:
                    # The list is full
                    status_list = StatusList2021()
                    next_index = 0
                else:
                    next_index = status_list.current_index + 1
                status_list.current_index = next_index
                status_list.save()
                payload["listIndex"] = next_index
                payload["listId"] = "/credentials/status/list/" + str(status_list.id)
                payload["listProxy"] = proxy.proxy_id
        else:
            accreditation = PotentialAccreditationInformation.objects.filter(
                type=vc_specific_types[0]
            ).first()
            if not accreditation:
                raise BadRequest(_("Invalid credential types"))

        try:
            response = requests.request("POST", url, headers=headers, json=payload)
        except Exception as e:
            raise Exception(e)
        content = json.loads(response.content.decode("utf-8"))
        credential = None
        if "credential" in content:
            jwt_decoded = jwt.api_jwt.decode_complete(
                content["credential"],
                "",
                algorithms=["ES256"],
                options={"verify_signature": False},
            )
            payload = jwt_decoded.get("payload")
            vc_content = payload["vc"]
            credential = vc_content
            credential_status = None
            status_type = None
            if vc_content.get("credentialStatus"):
                credential_status = vc_content.get("credentialStatus")
                status_type = credential_status["type"]
            # IssuedVC Instance creation
            issued_vc = IssuedVerifiableCredential(
                vc_id=vc_content["id"].split("urn:uuid:")[1],
                vc_type=request_post["types"],
                hash=None,
                issuance_date=vc_content["issuanceDate"],
                status=False,
                revocation_type=status_type,
                revocation_info=credential_status,
                holder=vc_content["credentialSubject"]["id"],
            )
            issued_vc.save()

        return_dict = {
            "status_code": response.status_code,
            "content": content,
            "credential": credential,
        }
        return return_dict
