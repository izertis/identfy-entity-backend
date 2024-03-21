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


class CredentialResponseSerializer(serializers.Serializer):
    format = serializers.CharField(
        max_length=255, default="jwt_vc", required=False
    )
    credential = serializers.CharField(max_length=1255, required=False)
    acceptance_token = serializers.CharField(max_length=1255, required=False)
    c_nonce = serializers.CharField(max_length=255, required=False)
    c_nonce_expires_in = serializers.IntegerField(required=False)


class ExternalDataResponse(serializers.Serializer):
    credential_data = serializers.JSONField(
        help_text="Credential data", required=False
    )
    deferred_tx_id = serializers.CharField(max_length=1255, required=False)
    schema_addr = serializers.CharField(max_length=1255, required=False)


class ResponseSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=4)
    content = serializers.JSONField()


class DeferredRegistry(serializers.Serializer):
    client_id = serializers.CharField(max_length=255)
    vc_type = serializers.CharField(max_length=255)
    pin = serializers.CharField(max_length=255)
