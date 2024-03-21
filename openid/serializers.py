from rest_framework import serializers

from .models import (
    CredentialIssuerMetadata,
    IssuanceCredentialOffer,
    NonceManager,
    PresentationDefinition,
    VCScopeAction,
    VPScopeAction,
)


class IssuanceCredentialOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuanceCredentialOffer
        fields = ("credential_offer",)


class QrSerializer(serializers.Serializer):
    qr = serializers.ImageField()


class IssuanceOfferResponse(serializers.Serializer):
    credential_offer = serializers.JSONField()
    user_pin = serializers.IntegerField(required=False)


class CredentialIssuerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialIssuerMetadata
        fields = (
            "authorization_server",
            "credential_issuer",
            "credential_endpoint",
            "deferred_credential_endpoint",
            "credentials_supported",
        )


class AuthorizationServerSerializer(serializers.Serializer):
    issuer = serializers.CharField(max_length=1255)
    authorization_endpoint = serializers.CharField(max_length=1255)
    token_endpoint = serializers.CharField(max_length=1255)
    direct_post_endpoint = serializers.CharField(max_length=1255)
    jwks_uri = serializers.CharField(max_length=1255)
    scopes_supported = serializers.ListField()
    response_types_supported = serializers.ListField()
    response_modes_supported = serializers.ListField()
    grant_types_supported = serializers.ListField()
    subject_types_supported = serializers.ListField()
    id_token_signing_alg_values_supported = serializers.ListField()
    request_object_signing_alg_values_supported = serializers.ListField()
    request_parameter_supported = serializers.BooleanField()
    request_uri_parameter_supported = serializers.BooleanField()
    token_endpoint_auth_methods_supported = serializers.ListField()
    vp_formats_supported = serializers.ListField()
    subject_syntax_types_supported = serializers.ListField()
    subject_trust_frameworks_supported = serializers.ListField()
    id_token_types_supported = serializers.ListField()


class AuthorizeResponseSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=1255)


class CreatedDirectPostSerializer(serializers.Serializer):
    id_token = serializers.CharField(max_length=1255, required=False)
    vp_token = serializers.CharField(max_length=1255, required=False)
    presentation_submission = serializers.CharField(
        max_length=1255, required=False
    )


class TokenRequestSerializer(serializers.Serializer):
    grant_type = serializers.CharField(
        max_length=1255,
        default="authorization_code",
        help_text="It can be authorization_code or urn:ietf:params:oauth:grant-type:pre-authorized_code",
    )
    client_id = serializers.CharField(
        max_length=1255, help_text="The client identifier"
    )
    code = serializers.CharField(
        max_length=1255, help_text="The authorization code", required=False
    )
    code_verifier = serializers.CharField(
        max_length=1255,
        help_text="The code verifier for the PKCE request",
        required=False,
    )
    pre_authorized_code = serializers.CharField(
        source="pre-authorized_code",
        max_length=1255,
        help_text="The pre-authorised code",
        required=False,
    )
    user_pin = serializers.IntegerField(help_text="User pin", required=False)


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=1255)
    token_type = serializers.CharField(max_length=1255)
    expires_in = serializers.IntegerField()
    c_nonce = serializers.CharField(max_length=1255)
    c_nonce_expires_in = serializers.IntegerField()


class CredentialRequestSerializer(serializers.Serializer):
    types = serializers.CharField(
        max_length=1255, help_text="Credential types requested"
    )
    format = serializers.CharField(
        max_length=255,
        default="jwt_vc",
        help_text="Format of the returned credentials",
    )
    proof = serializers.JSONField(
        help_text="Proof object containing proof_type and jwt"
    )


class CredentialResponseSerializer(serializers.Serializer):
    format = serializers.CharField(max_length=255, default="jwt_vc")
    credential = serializers.CharField(
        max_length=1255,
        default="LUpixVCWJk0eOt4CXQe1NXK....WZwmhmn9OQp6YxX0a2L",
    )
    c_nonce = serializers.CharField(max_length=255)
    c_nonce_expires_in = serializers.IntegerField()


class PublicJwkSerializer(serializers.Serializer):
    keys = serializers.CharField(max_length=2255)


class ClaimsVerificationSerializer(serializers.Serializer):
    verified = serializers.BooleanField()


class PresentationDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationDefinition
        fields = "__all__"


class ResponseSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=4)
    content = serializers.DictField()


class NonceManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonceManager
        fields = "__all__"


class VCScopeActionSerializer(serializers.ModelSerializer):
    presentation_definition = PresentationDefinitionSerializer(read_only=True)

    class Meta:
        model = VCScopeAction
        fields = [
            "scope",
            "response_type",
            "is_deferred",
            "credential_types",
            "credential_schema_address",
            "presentation_definition",
            "entity",
        ]


class VPScopeActionSerializer(serializers.ModelSerializer):
    presentation_definition = PresentationDefinitionSerializer(read_only=True)

    class Meta:
        model = VPScopeAction
        fields = [
            "scope",
            "response_type",
            "presentation_definition",
            "entity",
        ]
