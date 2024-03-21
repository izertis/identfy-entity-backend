from __future__ import annotations

import ast
import json
import urllib.parse
from typing import Any, List

import requests
from django.conf import settings
from django.core.exceptions import BadRequest

from .abstractions import AOpenidService
from .models import (
    CredentialIssuerMetadata,
    IssuanceCredentialOffer,
    PresentationDefinition,
    VerifierMetadata,
)
from .serializers import (
    AuthorizationServerSerializer,
    CreatedDirectPostSerializer,
    IssuanceCredentialOfferSerializer,
    IssuanceOfferResponse,
    ResponseSerializer,
)


class OpenidService(AOpenidService):
    @staticmethod
    def get_credential_offer_by_pk(
        pre_authorized_code: str | None, user_pin_required: bool | None
    ) -> dict | IssuanceOfferResponse | None:
        offer = IssuanceCredentialOffer.objects.filter(pk=settings.DID).first()

        if not offer:
            return None
        else:
            credential_offer = ast.literal_eval(offer.credential_offer)

            if pre_authorized_code:
                credential_offer["grants"] = {
                    "urn:ietf:params:oauth:grant-type:pre-authorized_code": {
                        "pre-authorized_code": pre_authorized_code,
                        "user_pin_required": bool(user_pin_required or False),
                    }
                }
            else:
                credential_offer["grants"] = {"authorization_code": {}}

            return {"credential_offer": credential_offer}

    @staticmethod
    def get_credential_offer_by_issuer(
        pre_authorized_code: str | None,
        user_pin_required: bool | None,
    ) -> dict | IssuanceCredentialOfferSerializer | None:

        url = settings.BACKEND_DOMAIN + "/offers"

        if pre_authorized_code:
            req = requests.models.PreparedRequest()
            req.prepare_url(
                url,
                {
                    "pre-authorized_code": pre_authorized_code,
                    "user_pin_required": user_pin_required,
                },
            )
            url = req.url
        get_offer_uri = urllib.parse.quote_plus(url)
        complete_url = (
            "openid-credential-offer://?credential_offer_uri=" + get_offer_uri
        )

        return {"credential_offer": complete_url}

    @staticmethod
    def get_credential_issuer_metadata_by_issuer(
        issuer_id: str,
    ) -> CredentialIssuerMetadata | None:
        all_issuers_metadata = CredentialIssuerMetadata.objects.filter(
            issuer=issuer_id
        )
        credentials_supported = []
        for metadata in all_issuers_metadata:
            for credential in metadata.credentials_supported:
                credentials_supported.append(credential)

        metadata = all_issuers_metadata.first()
        metadata.credentials_supported = credentials_supported

        return metadata

    @staticmethod
    def get_authorization_server_metadata(
        issuer_id: str,
    ) -> AuthorizationServerSerializer | None:
        url = (
            settings.CREDENTIALS_URL + "/auth/.well-known/openid-configuration"
        )

        verifier_scopes_by_issuer = (
            OpenidService._get_verifiers_metadata_scopes_by_issuer(issuer_id)
        )
        params = {"issuerUri": settings.BACKEND_DOMAIN}
        try:
            response = requests.request("GET", url, params=params)
        except Exception as e:
            raise Exception(e)

        if response.status_code == 200:
            content = json.loads(response.content.decode("utf-8"))
            content["scopes_supported"] += verifier_scopes_by_issuer
            return_dict = content

            return return_dict
        else:
            raise BadRequest({"status_code": response.status_code})

    @staticmethod
    def _get_verifiers_metadata_scopes_by_issuer(issuer_id: str) -> List[str]:
        verifier_by_issuer = VerifierMetadata.objects.filter(verifier=issuer_id)
        result = []
        for metadata in verifier_by_issuer:
            result.append(metadata.scope)
        return result

    @staticmethod
    def authorize(request: Any) -> ResponseSerializer | None:
        private_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        public_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        url = settings.CREDENTIALS_URL + "/auth/authorize"
        request_get = request.GET

        params = {
            "response_type": request_get["response_type"],
            "scope": request_get["scope"],
            "state": request_get["state"],
            "client_id": request_get["client_id"],
            "redirect_uri": request_get["redirect_uri"],
            "nonce": request_get.get("nonce"),
            "code_challenge": request_get.get("code_challenge"),
            "code_challenge_method": request_get.get("code_challenge_method"),
            "authorization_details": request_get.get("authorization_details"),
            "client_metadata": request_get["client_metadata"],
            "issuerUri": settings.BACKEND_DOMAIN,
            "privateKeyJwk": json.dumps(private_key_jwk),
            "publicKeyJwk": json.dumps(public_key_jwk),
        }
        if request_get.get("issuer_state") != None:
            params["issuer_state"] = request_get.get("issuer_state")

        if not params["authorization_details"]:
            # Must be verifier
            verifier_scopes_by_issuer = (
                OpenidService._get_verifiers_metadata_scopes_by_issuer(
                    settings.DID
                )
            )
            is_verifier = bool(verifier_scopes_by_issuer)
            if not is_verifier:
                raise BadRequest(
                    {
                        "status_code": 400,
                        "message": "Authorization details not present in authorization request",
                    }
                )
            if not params["scope"] in verifier_scopes_by_issuer:
                raise BadRequest(
                    {
                        "status": 400,
                        "message": "Unsupported scope for verification process",
                    }
                )
            params["requested_response_type"] = "vp_token"
            presentation_definition = PresentationDefinition.objects.filter(
                scope=params["scope"]
            ).first()
            params["definition_id"] = presentation_definition.id
        else:
            all_issuers_metadata = CredentialIssuerMetadata.objects.filter(
                issuer=settings.DID
            )
            credentials_supported = []
            for metadata in all_issuers_metadata:
                tmp = metadata.credentials_supported
                for credential in tmp:
                    credentials_supported.extend((credential["types"]))
            # Must be issuer
            auth_details = json.loads(params["authorization_details"])
            for detail in auth_details:
                credentials_requested = detail["types"]
                if len(
                    set(credentials_supported).intersection(
                        set(credentials_requested)
                    )
                ) != len(credentials_requested):
                    raise BadRequest(
                        {
                            "status": 400,
                            "message": "Unsupported credentials for issuance process",
                        }
                    )
            params["requested_response_type"] = "id_token"

        try:
            response = requests.request("GET", url, params=params)
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict

    @staticmethod
    def direct_post(
        request: CreatedDirectPostSerializer,
    ) -> ResponseSerializer:

        private_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        url = settings.CREDENTIALS_URL + "/auth/direct_post"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "issuerUri": settings.BACKEND_DOMAIN,
            "privateKeyJwk": json.dumps(private_key_jwk),
            "vp_token": request.get("vp_token") or None,
            "id_token": request.get("id_token") or None,
            "presentation_submission": request.get("presentation_submission")
            or None,
            "verifier_id": settings.DID if request.get("vp_token") else None,
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict

    @staticmethod
    def token_request(request: Any) -> ResponseSerializer:
        private_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        public_key_jwk = ast.literal_eval(settings.PUBLIC_KEY)
        url = settings.CREDENTIALS_URL + "/auth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {
            "grant_type": request.get("grant_type"),
            "client_id": request.get("client_id"),
            "code": request.get("code") or None,
            "code_verifier": request.get("code_verifier") or None,
            "pre-authorized_code": request.get("pre-authorized_code") or None,
            "user_pin": request.get("user_pin") or None,
            "issuerUri": settings.BACKEND_DOMAIN,
            "privateKeyJwk": json.dumps(private_key_jwk),
            "publicKeyJwk": json.dumps(public_key_jwk),
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict

    @staticmethod
    def get_public_jwk_by_issuer() -> dict | None:
        # SUPPORTS ONLY CRV
        public_key_jwk = ast.literal_eval(settings.PUBLIC_KEY)
        response = {
            "keys": [
                {
                    "kty": public_key_jwk["kty"],
                    "crv": public_key_jwk["crv"] or None,
                    "alg": public_key_jwk["alg"],
                    "x": public_key_jwk["x"] or None,
                    "y": public_key_jwk["y"] or None,
                    "kid": public_key_jwk["kid"],
                }
            ]
        }
        return response

    @staticmethod
    def get_claims_validation(request: Any) -> dict | None:

        request_get = request.GET
        params = {"data": request_get["data"]}
        headers = {"Authorization": settings.EXTERNAL_API_KEY}
        try:
            response = requests.request(
                "GET", settings.EXTERNAL_URL, headers=headers, params=params
            )
        except Exception:
            # TODO: Mockupt implementation. Remove after its implementation
            return {"verified": True}
        if response.status_code == 200:
            return json.loads(response.content.decode("utf-8"))
        else:
            raise BadRequest({"status_code": response.status_code})

    @staticmethod
    def exchange_preauth(code: str) -> dict:

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
