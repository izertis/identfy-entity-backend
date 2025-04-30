from __future__ import annotations

import base64
import gzip
import json
from typing import Any, List

import jwt
import requests

from credentials.constants import EBSI_VC_TYPE
from credentials.models import IssuedVerifiableCredential, StatusList2021
from credentials.strategy import CredentialStrategy
from ebsi.enums import AccreditationTypes
from ebsi.models import EbsiAccreditationWhiteList
from ebsi.service import EbsiService
from project import settings

from .abstractions import ACredentialService
from .serializers import (
    ChangeStatus,
    CredentialResponseSerializer,
    DeferredRegistry,
    EbsiCredentialRequestSerializer,
    ExternalDataResponse,
    ResponseSerializer,
)


class CredentialService(ACredentialService):
    @staticmethod
    def credentials(
        request: list | EbsiCredentialRequestSerializer,
        token: str,
    ) -> List[ResponseSerializer] | ResponseSerializer | None:
        response: ResponseSerializer = {}
        strategy = CredentialStrategy(request, token)
        credential = None
        # TODO: EBSI requires an did:key for the conformance test but
        # in production it should always be a did:ebsi
        ebsi_strategy = strategy.ebsi_credentials()
        response = {
            "status_code": ebsi_strategy["status_code"],
            "content": ebsi_strategy["content"],
        }
        credential = ebsi_strategy["credential"]

        if credential:
            CredentialService.__register_openid_vc_id(credential, token)

        return response

    @staticmethod
    def __register_openid_vc_id(credential, token=None):
        # TODO: This must change in the future. Part of this code should be moved to VC Service
        # This access_token should be looked at

        types = credential["type"]
        vc_type = None
        for type in types:
            if type not in EBSI_VC_TYPE:
                vc_type = type
                break

        pre_code = ""
        if token:
            token_decoded = jwt.api_jwt.decode_complete(
                token.replace("Bearer", "").replace("BEARER", "").lstrip(),
                "",
                algorithms=["ES256"],
                options={"verify_signature": False},
            )
            payload = token_decoded.get("payload")
            if not payload["sub"].startswith("did:"):
                pre_code = payload["sub"]

        payload = {
            "vc_id": credential["id"].split("urn:uuid:")[1],
            "vc_type": vc_type,
            "pre_code": pre_code,
            "did": credential["credentialSubject"]["id"],
            "issuance_date": credential["issuanceDate"],
            "nbf": credential["validFrom"],
        }
        if credential.get("expirationDate") is not None:
            payload["expiration_date"] = credential.get("expirationDate")
        try:
            headers = {}
            if settings.ENTITY_API_KEY:
                headers = {"X-API-KEY": settings.ENTITY_API_KEY}
            requests.request(
                "POST",
                settings.ENTITY_URL + "/credentials/external-data",
                headers=headers,
                json=payload,
            )
        except Exception:
            pass

    @staticmethod
    def deferred_credentials(
        token: str,
    ) -> CredentialResponseSerializer | None:
        url = settings.VC_SERVICE_URL + "/credential_deferred"
        headers = {
            "Authorization": token,
        }

        payload = {
            "issuerUri": settings.BACKEND_DOMAIN + "/",
            "issuerDid": settings.DID,
        }
        try:
            response = requests.request("POST", url, headers=headers, json=payload)
        except Exception as e:
            raise Exception(e)
        content = None
        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
        if "credential" in content:
            jwt_decoded = jwt.api_jwt.decode_complete(
                content["credential"],
                "",
                algorithms=None,
                options={"verify_signature": False},
            )
            payload = jwt_decoded.get("payload")
            vc_content = payload["vc"]
            vc_types = vc_content["type"]
            credential_status = None
            status_type = None
            if vc_content.get("credentialStatus"):
                credential_status = vc_content.get("credentialStatus")
                status_type = credential_status["type"]
            # IssuedVC Instance creation
            issued_vc = IssuedVerifiableCredential(
                vc_id=vc_content["id"].split("urn:uuid:")[1],
                vc_type=vc_types,
                hash=None,
                issuance_date=vc_content["issuanceDate"],
                status=False,
                revocation_type=status_type,
                revocation_info=credential_status,
            )
            issued_vc.save()
            CredentialService.__register_openid_vc_id(vc_content)

        return content

    @staticmethod
    def external_data(
        vc_type: str, user_id: str | None, pin: str | None
    ) -> ExternalDataResponse | None:
        if vc_type in AccreditationTypes.values():
            # We don't need to ask an external source
            white_list = EbsiAccreditationWhiteList.objects.filter(
                type=vc_type, did=user_id
            ).first()
            if white_list is None:
                return {
                    "status_code": 403,
                    "content": "Invalid DID for the requested VC",
                }
            accredited_for_content = []
            schemas = white_list.schema.all()
            terms_of_use = []
            for information in schemas:
                if information.accredited_schema is not None:
                    accredited_for_content.append(
                        {
                            "types": information.accredited_for,
                            "schemaId": information.accredited_schema,
                        }
                    )
                terms_of_use.append(information.attribute_id)
            body = {
                "accreditedFor": accredited_for_content,
                # "reservedAttributeId": "WIP-ATTRIBUTE-ID" # TODO: Change after tasks related to register VCs in EBSI are done
            }
            if (
                vc_type == AccreditationTypes.VerifiableAccreditationToAttest
                or vc_type == AccreditationTypes.VerifiableAccreditationToAccredit
            ):
                attribute_id = EbsiService.trusted_issuer_registry(
                    user_id, terms_of_use[0], vc_type
                )
                body["reservedAttributeId"] = attribute_id
            content = {"body": body, "termsOfUse": terms_of_use}
            return {"status_code": 200, "content": content}
        if not settings.ENTITY_URL and settings.DEVELOPER_MOCKUP_ENTITIES:
            # Return empty data
            body = {}
            status_code = 200
        else:
            params = {"vc_type": vc_type, "user_id": user_id, "pin": pin}
            headers = {}
            if settings.ENTITY_API_KEY:
                headers = {"X-API-KEY": settings.ENTITY_API_KEY}
            try:
                response = requests.request(
                    "GET",
                    settings.ENTITY_URL + "/credentials/external-data",
                    headers=headers,
                    params=params,
                    verify=False,
                )
            except Exception as e:
                raise Exception(e)

            body = json.loads(response.content.decode("utf-8"))
            status_code = response.status_code

        return_dict = {"status_code": status_code, "content": {"body": body}}
        return return_dict

    @staticmethod
    def register_deferred(request: DeferredRegistry) -> dict:
        if not settings.ENTITY_URL and settings.DEVELOPER_MOCKUP_ENTITIES:
            # Return empty data
            content = "DEV_CODE"
            status_code = 200
        else:
            payload = request
            try:
                headers = {}
                if settings.ENTITY_API_KEY:
                    headers = {"X-API-KEY": settings.ENTITY_API_KEY}
                response = requests.request(
                    "POST",
                    settings.ENTITY_URL + "/deferred/registry",
                    headers=headers,
                    json=payload,
                )
            except Exception as e:
                raise Exception(e)

            content = response.content.decode("utf-8")
            status_code = response.status_code

        return_dict = {"status_code": status_code, "content": content}
        return return_dict

    @staticmethod
    def exchange_deferred(code: str) -> dict:
        if not settings.ENTITY_URL and settings.DEVELOPER_MOCKUP_ENTITIES:
            # Return empty data
            content = {"data": {}}
            status_code = 200
        else:
            try:
                headers = {}
                if settings.ENTITY_API_KEY:
                    headers = {"X-API-KEY": settings.ENTITY_API_KEY}
                response = requests.request(
                    "GET",
                    settings.ENTITY_URL + "/deferred/exchange/" + code,
                    headers=headers,
                )
            except Exception as e:
                raise Exception(e)

            content = json.loads(response.content.decode("utf-8"))
            status_code = response.status_code

        return_dict = {"status_code": status_code, "content": content}
        return return_dict

    @staticmethod
    def issue_status_credential(status_list: StatusList2021) -> dict:
        # GET STATUS LIST AND FILL PARAMS
        # status_list = issued_vc.status_list
        compressed_list = gzip.compress(status_list.content)
        base64url_compressed_list = base64.b64encode(compressed_list)

        url = settings.VC_SERVICE_URL + "/credentials/status"
        params = {
            "issuerDid": settings.DID,
            "issuerUri": settings.BACKEND_DOMAIN,
            "listId": settings.BACKEND_DOMAIN
            + "/credentials/status/list/"
            + str(status_list.id),
            "statusPurpose": "revocation",  # TODO: This could be configurable
            "statusList": base64url_compressed_list.decode("utf-8"),
            "revocationType": "StatusList2021",
        }

        try:
            response = requests.request("POST", url, json=params)
        except Exception as e:
            raise Exception(e)

        return_dict = {
            "status_code": response.status_code,
            "content": response.content.decode("utf-8"),
        }
        return return_dict

    @staticmethod
    def ebsi_accreditation_direct_issuance(request: Any) -> dict:
        url = settings.VC_SERVICE_URL + "/ebsi/accreditation/issuance"
        request_get = request.GET
        type = request_get.get("type")
        holder = request_get.get("holder")
        if type is None or holder is None:
            return {
                "status_code": 400,
                "content": "Missing 'type' or 'holder' parameter",
            }
        params = {
            "issuerDid": settings.DID,
            "issuerUri": settings.BACKEND_DOMAIN,
            "accreditationType": type,
            "holderDid": holder,
        }
        try:
            response = requests.request("GET", url, params=params)
        except Exception as e:
            raise Exception(e)
        return_dict = {
            "status_code": response.status_code,
            "content": json.loads(response.content.decode("utf-8")),
        }
        return return_dict

    @staticmethod
    def change_credential_status(
        vc: IssuedVerifiableCredential, request: ChangeStatus
    ) -> dict:
        if vc.status:
            return {"status_code": 200, "message": "Previusly Revoked"}

        if request.get("status") == "revoked":
            vc.status = True
            vc.save()
        else:
            return {"status_code": 400, "message": "Not a valid Status"}

        return {"status_code": 200, "message": "OK"}
