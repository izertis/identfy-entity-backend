import ast
import json

import requests

from credentials.serializers import (
    EbsiCredentialRequestSerializer,
    ResponseSerializer,
)
from project import settings


class CredentialStrategy:
    def __init__(self, request, token):
        self.request = request
        self.token = token

    def ebsi_credentials(self) -> ResponseSerializer:

        private_key_jwk = ast.literal_eval(settings.PRIVATE_KEY)
        public_key_jwk = ast.literal_eval(settings.PUBLIC_KEY)
        url = settings.CREDENTIALS_URL + "/credentials"
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
            "privateKeyJwk": private_key_jwk,
            "publicKeyJwk": public_key_jwk,
        }

        try:
            response = requests.request(
                "POST", url, headers=headers, json=payload
            )
        except Exception as e:
            raise Exception(e)

        content = json.loads(response.content.decode("utf-8"))

        return_dict = {"status_code": response.status_code, "content": content}
        return return_dict
