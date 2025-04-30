from rest_framework import serializers


class EbsiCredentialRequestSerializer(serializers.Serializer):
    types = serializers.JSONField(help_text="Credential types requested")
    format = serializers.CharField(
        max_length=255,
        default="jwt_vc",
        help_text="Format of the returned credentials",
    )
    proof = serializers.JSONField(
        help_text="Proof object containing proof_type and jwt"
    )


class ResolveCredentialOfferSerializer(serializers.Serializer):
    credential_offer = serializers.CharField(
        help_text="Credential Offer from a VC Issuer",
    )


class ResolveCredentialOfferResponseSerializer(serializers.Serializer):
    credential_issuer = (
        serializers.CharField(
            max_length=2000,
            help_text="VC Issuer URI",
        ),
    )
    credentials = (serializers.JSONField(help_text="Credentials supported"),)
    grants = (serializers.JSONField(help_text="Grant types supported"),)


class RequestVcSerializer(serializers.Serializer):
    credential_offer = serializers.CharField(
        help_text="Credential Offer from a VC Issuer",
    )
    vc_type = serializers.ListField(
        child=serializers.CharField(),
        help_text="Types of the VC to request",
    )
    pin_code = serializers.IntegerField(required=False)


class RequestVcResponseSerializer(serializers.Serializer):
    credential = serializers.CharField(
        help_text="Credential Offer from a VC Issuer", required=False
    )
    acceptance_token = serializers.CharField(
        help_text="Exchange Code for a Deferred VC", required=False
    )


class RequestDeferredVcSerializer(serializers.Serializer):
    issuer = serializers.CharField(
        help_text="VC Issuer URI",
    )
    acceptanceToken = serializers.CharField(
        help_text="Token to exchange for the VC",
    )


class CredentialResponseSerializer(serializers.Serializer):
    format = serializers.CharField(max_length=255, default="jwt_vc", required=False)
    credential = serializers.CharField(max_length=1255, required=False)
    acceptance_token = serializers.CharField(max_length=1255, required=False)
    c_nonce = serializers.CharField(max_length=255, required=False)
    c_nonce_expires_in = serializers.IntegerField(required=False)


class ExternalDataResponse(serializers.Serializer):
    credential_data = serializers.JSONField(help_text="Credential data", required=False)
    schema_addr = serializers.CharField(max_length=1255, required=False)


class ResponseSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=4)
    content = serializers.JSONField()


class DeferredRegistry(serializers.Serializer):
    client_id = serializers.CharField(max_length=255)
    vc_type = serializers.CharField(max_length=255)
    pin = serializers.CharField(max_length=255, required=False)


class ChangeStatus(serializers.Serializer):
    status = serializers.CharField(
        max_length=255,
        help_text="revoke",
    )
