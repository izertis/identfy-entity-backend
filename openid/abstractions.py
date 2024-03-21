from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from .models import CredentialIssuerMetadata
from .serializers import (
    AuthorizeResponseSerializer,
    CreatedDirectPostSerializer,
    IssuanceCredentialOfferSerializer,
    IssuanceOfferResponse,
    ResponseSerializer,
    TokenRequestSerializer,
)


class AOpenidService(ABC):
    @staticmethod
    @abstractmethod
    def get_credential_offer_by_pk(
        pre_authorized_code: str | None, user_pin_required: bool | None
    ) -> dict | IssuanceOfferResponse | None: ...

    @staticmethod
    @abstractmethod
    def get_credential_offer_by_issuer(
        pre_authorized_code: str | None,
        user_pin_required: bool | None,
    ) -> dict | IssuanceCredentialOfferSerializer | None: ...

    @staticmethod
    @abstractmethod
    def get_credential_issuer_metadata_by_issuer(
        issuer_id: str,
    ) -> CredentialIssuerMetadata | None: ...

    @staticmethod
    @abstractmethod
    def get_authorization_server_metadata(
        issuer_id: str,
    ) -> AuthorizeResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def _get_verifiers_metadata_scopes_by_issuer(
        issuer_id: str,
    ) -> List[str]: ...

    @staticmethod
    @abstractmethod
    def authorize(request: Any) -> ResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def direct_post(
        request: CreatedDirectPostSerializer,
    ) -> ResponseSerializer: ...

    @staticmethod
    @abstractmethod
    def token_request(request: Any) -> ResponseSerializer: ...

    @staticmethod
    @abstractmethod
    def get_public_jwk_by_issuer() -> dict | None: ...

    @staticmethod
    @abstractmethod
    def get_claims_validation(request: Any) -> dict | None: ...
    @staticmethod
    @abstractmethod
    def exchange_preauth(code: str) -> dict: ...
