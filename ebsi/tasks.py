import jwt
import requests
from celery import chain, shared_task

from common.services.rpc_service import RpcService
from ebsi.enums import EbsiDidDocumentsRelationships
from ebsi.services.ebsi_api_service import EbsiApiService
from project import settings

from .models import ProxyAPIs


@shared_task()
def onboard_ebsi_entity(vc: str):
    chain(
        register_ebsi_did.si(vc),
        register_verification_method.si(),
        register_verification_relationship.si(
            EbsiDidDocumentsRelationships.Authentication
        ),
        register_verification_relationship.si(
            EbsiDidDocumentsRelationships.AssertionMethod,
        ),
    ).delay()


@shared_task()
def register_trusted_entity_and_proxy_api(vc: str):
    chain(
        resgister_trusted_entity.si(vc),
        register_proxy_revocation_api.si(),
    ).delay()


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=15,
)
def register_ebsi_did(vc: str):
    # First we check if the entity is already registered
    try:
        EbsiApiService.get_did(settings.DID)
        return
    except requests.HTTPError as e:
        if e.response.status_code != 404:
            raise e

    body = {
        "jsonrpc": "2.0",
        "method": "onboardDid",
        "params": {
            "vc": vc,
            "did": settings.DID,
            "url": settings.BACKEND_DOMAIN,
        },
    }
    RpcService(body).send_request()


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=15,
)
def register_verification_method():
    body = {
        "jsonrpc": "2.0",
        "method": "addVerificationMethod",
        "params": {
            "did": settings.DID,
            "url": settings.BACKEND_DOMAIN,
        },
    }
    RpcService(body).send_request()


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=15,
)
def register_verification_relationship(
    relationship: EbsiDidDocumentsRelationships,
):
    body = {
        "jsonrpc": "2.0",
        "method": "addVerificationRelationship",
        "params": {
            "name": relationship,
            "did": settings.DID,
            "url": settings.BACKEND_DOMAIN,
        },
    }
    RpcService(body).send_request()


def extract_attribute_from_vc(vc: str) -> str:
    jwt_decoded = jwt.api_jwt.decode_complete(
        vc,
        "",
        algorithms=["ES256", "ES256K"],
        options={"verify_signature": False},
    )
    payload = jwt_decoded.get("payload")
    vc = payload.get("vc")
    credential_subject = vc.get("credentialSubject")
    attribute = credential_subject.get("reservedAttributeId")
    if attribute is None:
        raise Exception(
            "Bad formatted Accreidtattion VC - Missing 'reservedAttributeId'"
        )
    return attribute


def check_if_attribute_already_fill(data) -> bool:
    return data["attribute"]["body"] != ""


# TODO. Most probably these tasks don't need autoretry. If they failed one, most probably they will fail again.
@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=15,
)
def resgister_trusted_entity(vc: str):
    # We should check if the VC is already registered
    attribute_id = extract_attribute_from_vc(vc)
    try:
        attribute = EbsiApiService.get_issuer_attribute(settings.DID, attribute_id)
        if check_if_attribute_already_fill(attribute):
            return
    except requests.HTTPError as e:
        if e.response.status_code != 404:
            raise e

    body = {
        "jsonrpc": "2.0",
        "method": "setTrustedIssuerData",
        "params": {
            "did": settings.DID,
            "vc": vc,
            "url": settings.BACKEND_DOMAIN,
        },
    }
    RpcService(body).send_request()


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=15,
)
def register_proxy_revocation_api():
    from credentials.models import StatusList2021

    if ProxyAPIs.objects.first() is None:
        status_list = StatusList2021(current_index=0)
        status_list.save()
        body = {
            "jsonrpc": "2.0",
            "method": "addIssuerProxy",
            "params": {
                "did": settings.DID,
                "prefix": settings.BACKEND_DOMAIN,
                "testSuffix": "/credentials/status/list/" + str(status_list.id),
                "url": settings.BACKEND_DOMAIN,
            },
        }
        response = RpcService(body).send_request()
        ProxyAPIs(proxy_id=response["content"]["result"]).save()
