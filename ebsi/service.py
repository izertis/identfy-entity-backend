from __future__ import annotations

from common.services.rpc_service import RpcService
from common.utils.hex_utils import append_hex_prefix
from ebsi.enums import AccreditationTypes
from project import settings
from project.settings import BACKEND_DOMAIN


class EbsiService:
    @staticmethod
    def trusted_issuer_registry(did: str, tao_attribute_id: str, vc_type: str) -> str:
        if not tao_attribute_id.startswith("0x"):
            tao_attribute_id = "0x" + tao_attribute_id

        if vc_type == AccreditationTypes.VerifiableAccreditationToAttest:
            issuer_type = "TrustedIssuer"
        elif vc_type == AccreditationTypes.VerifiableAccreditationToAccredit:
            issuer_type = "Tao"
        else:
            raise Exception("Invalid Issuer Type")
        body = {
            "jsonrpc": "2.0",
            "method": "addTrustedIssuer",
            "params": {
                "url": BACKEND_DOMAIN,
                "did": did,
                "taoDid": settings.DID,
                "taoAttributeId": append_hex_prefix(tao_attribute_id),
                "issuerType": issuer_type,
            },
        }

        rpc_response = RpcService(body).send_request()
        content = rpc_response.get("content")
        return content.get("result")

    @staticmethod
    def revoke_accreditation(did: str, tao_attribute_id: str, revision_id: str) -> str:
        if not tao_attribute_id.startswith("0x"):
            tao_attribute_id = "0x" + tao_attribute_id

        body = {
            "jsonrpc": "2.0",
            "method": "revokeAccreditation",
            "params": {
                "url": BACKEND_DOMAIN,
                "did": did,
                "taoDid": settings.DID,
                "taoAttributeId": append_hex_prefix(tao_attribute_id),
                "revisionId": revision_id,
            },
        }

        rpc_response = RpcService(body).send_request()
        content = rpc_response.get("content")
        return content.get("result")
