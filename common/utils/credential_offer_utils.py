from openid.models import IssuanceFlow, IssuanceInformation


def extract_issuance_flows(
    offer: IssuanceInformation, requested_credentials: list[str]
):
    issuance_flows = IssuanceFlow.objects.filter(
        credential_types__in=requested_credentials
    )
    if len(issuance_flows) != len(requested_credentials):
        raise Exception("Invalid types specified")
    return issuance_flows


def check_requested_types_for_credential_offer(requested_credentials: list[str]):
    issuance_info = IssuanceInformation.objects.first()
    if not issuance_info:
        raise Exception("Credential-Offer not found")
    extract_issuance_flows(issuance_info, requested_credentials)


def generate_credential_offer(
    offer: IssuanceInformation, requested_credentials: list[str]
):
    issuance_flows = extract_issuance_flows(offer, requested_credentials)
    credentials_supported = []
    for flow in issuance_flows:
        credential_type = {
            "types": [
                "VerifiableCredential",
                "VerifiableAttestation",
                flow.credential_types,
            ],
            "format": "jwt_vc",  # Only support this format
        }
        credentials_supported.append(credential_type)
    offer.credential_issuer_metadata["credentials_supported"] = credentials_supported
    return offer
