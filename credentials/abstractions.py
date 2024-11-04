from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List

from credentials.serializers import CredentialResponseSerializer, ExternalDataResponse


class ACredentialService(ABC):
    @staticmethod
    @abstractmethod
    def credentials(
        request: Any,
        token: str,
    ) -> List[CredentialResponseSerializer] | CredentialResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def deferred_credentials(token: str) -> CredentialResponseSerializer | None: ...

    @staticmethod
    @abstractmethod
    def external_data(
        schema: str, user_id: str | None
    ) -> ExternalDataResponse | None: ...
