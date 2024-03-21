from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from credentials.serializers import (
    CredentialResponseSerializer,
    DeferredRegistry,
    EbsiCredentialRequestSerializer,
    ExternalDataResponse,
    ResponseSerializer,
)


class ACredentialService(ABC):
    @staticmethod
    @abstractmethod
    def credentials(
        request: list | EbsiCredentialRequestSerializer,
        token: str,
    ) -> List[ResponseSerializer] | ResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def deferred_credentials(
        token: str,
    ) -> CredentialResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def external_data(
        vc_type: str, user_id: str | None, pin: str | None
    ) -> ExternalDataResponse | None: ...

    @staticmethod
    @abstractmethod
    def register_deferred(request: DeferredRegistry) -> dict: ...

    @staticmethod
    @abstractmethod
    def exchange_deferred(code: str) -> dict: ...
