import json
from posixpath import join as urljoin

import requests

from project import settings


class EbsiApiService:

    @staticmethod
    def get_did(did: str) -> dict:
        try:
            url = urljoin(settings.EBSI_DIDR_URL, did)
            response = requests.request("GET", url)
        except Exception as e:
            raise Exception(e)
        content = json.loads(response.content.decode("utf-8"))
        return_dict = {"status_code": response.status_code, "content": content}
        if return_dict["status_code"] != 200:
            raise requests.HTTPError(response=response)
        return return_dict

    @staticmethod
    def get_issuer_attribute(did: str, attribute_id: str) -> dict:
        try:
            url = urljoin(
                settings.EBSI_TIR_URL, did, "attributes", attribute_id
            )
            response = requests.request("GET", url)
        except Exception as e:
            raise Exception(e)
        content = json.loads(response.content.decode("utf-8"))
        if response.status_code != 200:
            raise requests.HTTPError(response=response)
        return content
