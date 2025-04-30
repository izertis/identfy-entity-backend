import json

import requests

from common.error.http_error import HTTPError
from project import settings


class RpcService:
    def __init__(self, body):
        self.body: dict = body

    def send_request(self) -> dict:
        try:
            url = settings.VC_SERVICE_URL.replace("/api", "")
            response = requests.request("POST", url + "/rpc", json=self.body)
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))
        return_dict = {"status_code": response.status_code, "content": content}
        if return_dict["status_code"] != 200:
            raise HTTPError(
                status=response.status_code, content=content["error"]["data"]
            )
        return return_dict

    @staticmethod
    def from_request_vc_payload(
        offer: str, vc_type: list[str], did: str, pin_code: int = None
    ):
        params = {
            "credentialOffer": offer,
            "vcType": vc_type,
            "url": settings.BACKEND_DOMAIN,
            "did": did,
            "externalAddr": f"{settings.BACKEND_DOMAIN}",
        }
        if pin_code is not None:
            params["pinCode"] = pin_code
        body = {"jsonrpc": "2.0", "method": "requestVC", "params": params}
        return RpcService(body)

    @staticmethod
    def from_resolve_credential_offer_payload(offer: str):
        body = {
            "jsonrpc": "2.0",
            "method": "resolveCredentialOffer",
            "params": {
                "credentialOffer": offer,
            },
        }
        return RpcService(body)

    @staticmethod
    def from_request_deferred_vc_payload(issuer: str, token: str):
        body = {
            "jsonrpc": "2.0",
            "method": "requestDeferredVC",
            "params": {
                "issuer": issuer,
                "acceptanceToken": token,
            },
        }
        return RpcService(body)
