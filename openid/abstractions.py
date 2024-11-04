from __future__ import annotations

from abc import ABC, abstractmethod

from .serializers import (
    AuthorizeResponseSerializer,
    CreatedDirectPostSerializer,
    IssuanceCredentialOfferSerializer,
    ResponseSerializer,
    TokenRequestSerializer,
)


class AOpenidService(ABC):
    @staticmethod
    @abstractmethod
    def get_credential_offer_by_issuer(
        client_id: str | None,
    ) -> dict | IssuanceCredentialOfferSerializer | None: ...

    @staticmethod
    @abstractmethod
    def get_credential_offer_by_pk(pk: str, client_id: str | None) -> dict | None: ...

    @staticmethod
    @abstractmethod
    def get_credential_issuer_metadata_by_issuer() -> dict | None: ...

    @staticmethod
    @abstractmethod
    def get_authorization_server_metadata() -> AuthorizeResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def authorize(
        request: object,
    ) -> ResponseSerializer: ...

    @staticmethod
    @abstractmethod
    def direct_post(
        request: CreatedDirectPostSerializer,
    ) -> ResponseSerializer: ...

    @staticmethod
    @abstractmethod
    def token_request(
        request: TokenRequestSerializer,
    ) -> ResponseSerializer: ...

    @staticmethod
    @abstractmethod
    def get_public_jwk_by_issuer() -> dict | None: ...

    @staticmethod
    @abstractmethod
    def get_claims_validation(
        request: object,
    ) -> dict | None: ...
