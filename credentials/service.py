from __future__ import annotations

import ast
import json
from typing import List

import requests
from django.core.exceptions import BadRequest

from credentials.strategy import CredentialStrategy
from project import settings

from .abstractions import ACredentialService
from .serializers import (
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

        ebsi_strategy = strategy.ebsi_credentials()
        response = ebsi_strategy
        return response

    @staticmethod
    def deferred_credentials(token: str) -> CredentialResponseSerializer | None:

        private_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        public_key_jwk = ast.literal_eval(settings.PUBLIC_KEY)
        url = settings.CREDENTIALS_URL + "/credential_deferred"
        headers = {
            "Authorization": token,
        }

        payload = {
            "issuerUri": settings.BACKEND_DOMAIN,
            "issuerDid": settings.DID,
            "privateKeyJwk": private_key_jwk,
            "publicKeyJwk": public_key_jwk,
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, json=payload
            )
        except Exception as e:
            raise Exception(e)
        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            return_dict = content

            return return_dict
        else:
            raise BadRequest({"status_code": response.status_code})

    @staticmethod
    def external_data(
        vc_type: str, user_id: str | None, pin: str | None
    ) -> ExternalDataResponse | None:

        params = {"vc_type": vc_type, "user_id": user_id, "pin": pin}

        headers = {"Authorization": settings.EXTERNAL_API_KEY}
        try:
            response = requests.request(
                "GET",
                settings.EXTERNAL_URL + "credentials/external-data",
                headers=headers,
                params=params,
            )
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict

    @staticmethod
    def register_deferred(request: DeferredRegistry) -> dict:
        payload = request
        headers = {"Authorization": settings.EXTERNAL_API_KEY}
        try:
            response = requests.request(
                "POST",
                settings.EXTERNAL_URL + "/deferred/registry",
                headers=headers,
                json=payload,
            )
        except Exception as e:
            raise Exception(e)

        content = response.content.decode("utf-8")

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict

    @staticmethod
    def exchange_deferred(code: str) -> dict:
        headers = {"Authorization": settings.EXTERNAL_API_KEY}
        try:
            response = requests.request(
                "GET",
                settings.EXTERNAL_URL + "/deferred/exchange/" + code,
                headers=headers,
            )
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict
