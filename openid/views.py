from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from PIL import Image
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

from openid.models import (
    NonceManager,
    PresentationDefinition,
    VCScopeAction,
    VPScopeAction,
)
from openid.services.generateqr import GenerateQr
from project import settings

from .serializers import (
    AuthorizationServerSerializer,
    AuthorizeResponseSerializer,
    ClaimsVerificationSerializer,
    CreatedDirectPostSerializer,
    CredentialIssuerSerializer,
    IssuanceCredentialOfferSerializer,
    IssuanceOfferResponse,
    NonceManagerSerializer,
    PresentationDefinitionSerializer,
    PublicJwkSerializer,
    QrSerializer,
    TokenRequestSerializer,
    TokenResponseSerializer,
    VCScopeActionSerializer,
    VPScopeActionSerializer,
)
from .service import OpenidService


class OpenidView(ViewSet):
    permission_classes = (AllowAny,)
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "pre-authorized_code",
                openapi.IN_QUERY,
                description="Preauthorize code",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "user_pin_required",
                openapi.IN_QUERY,
                description="User pin required",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        operation_description="GET Credential Offer",
        responses={
            302: openapi.Response("", IssuanceCredentialOfferSerializer)
        },
    )
    @action(detail=False, methods=["get"], url_path="credential-offer/url")
    def get_credential_offer_same_device_by_issuer(self, request):
        credential_offer = OpenidService.get_credential_offer_by_issuer(
            request.GET.get("pre-authorized_code"),
            request.GET.get("user_pin_required"),
        )
        if credential_offer:
            return Response(
                headers={
                    "Location": IssuanceCredentialOfferSerializer(
                        credential_offer
                    ).data["credential_offer"]
                },
                status=status.HTTP_302_FOUND,
            )

        return HttpResponseNotFound("Credential Offer not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "pre-authorized_code",
                openapi.IN_QUERY,
                description="Preauthorize code",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "user_pin_required",
                openapi.IN_QUERY,
                description="User pin required",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        operation_description="GET Credential Offer QR",
        responses={200: openapi.Response("", QrSerializer)},
    )
    @action(detail=False, methods=["get"], url_path="credential-offer/qr")
    def get_credential_offer_cross_device_by_issuer(self, request):
        credential_offer = OpenidService.get_credential_offer_by_issuer(
            request.GET.get("pre-authorized_code"),
            request.GET.get("user_pin_required"),
        )
        if credential_offer:
            url = IssuanceOfferResponse(credential_offer).data
            qr: Image = GenerateQr(url["credential_offer"]).generate_qr()
            user_pin = url.get("user_pin")
            response = HttpResponse(content_type="image/png")
            qr.save(response, "PNG")
            response.headers["user_pin"] = user_pin
            return response

        return HttpResponseBadRequest("Credential Offer not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "pre-authorized_code",
                openapi.IN_QUERY,
                description="Preauthorize code",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "user_pin_required",
                openapi.IN_QUERY,
                description="User pin required",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
        operation_description="GET Credential Offer Json",
        responses={200: openapi.Response("", IssuanceOfferResponse)},
    )
    @action(detail=False, methods=["get"], url_path=r"offers")
    def get_credential_offer_by_pk(self, request):
        credential_offer = OpenidService.get_credential_offer_by_pk(
            request.GET.get("pre-authorized_code"),
            request.GET.get("user_pin_required"),
        )
        if credential_offer:
            return Response(
                IssuanceOfferResponse(credential_offer).data["credential_offer"]
            )

        return HttpResponseNotFound("Credential Offer not found.")

    @swagger_auto_schema(
        method="get",
        operation_description="GET Credential Issuer Metadata",
        responses={200: openapi.Response("", CredentialIssuerSerializer)},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=".well-known/openid-credential-issuer",
    )
    def get_credential_issuer_metadata_by_issuer(self, request):
        credential_issuer_metadata = (
            OpenidService.get_credential_issuer_metadata_by_issuer(settings.DID)
        )
        if credential_issuer_metadata:
            return Response(
                CredentialIssuerSerializer(credential_issuer_metadata).data
            )

        return HttpResponseNotFound("Credential Issuer metadata not found.")

    @swagger_auto_schema(
        method="get",
        operation_description="GET Authorization Server Metadata",
        responses={200: openapi.Response("", AuthorizationServerSerializer)},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=".well-known/openid-configuration",
    )
    def get_authorization_server_metadata(self, request):
        authorization_server_metadata = (
            OpenidService.get_authorization_server_metadata(settings.DID)
        )
        if authorization_server_metadata:
            return Response(
                AuthorizationServerSerializer(
                    authorization_server_metadata
                ).data
            )

        return HttpResponseNotFound("Authorization Server metadata not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                name="response_type",
                in_=openapi.IN_QUERY,
                description="MUST be code",
                type=openapi.TYPE_STRING,
                required=True,
                example="code",
            ),
            openapi.Parameter(
                name="scope",
                in_=openapi.IN_QUERY,
                description="MUST include openid",
                type=openapi.TYPE_STRING,
                required=True,
                example="openid",
            ),
            openapi.Parameter(
                name="issuer_state",
                in_=openapi.IN_QUERY,
                description="The state from the issuer",
                type=openapi.TYPE_STRING,
                required=False,
                example="tracker=vcfghhj",
            ),
            openapi.Parameter(
                name="state",
                in_=openapi.IN_QUERY,
                description="The state from the client",
                type=openapi.TYPE_STRING,
                required=True,
                example="client-state",
            ),
            openapi.Parameter(
                name="client_id",
                in_=openapi.IN_QUERY,
                description="The client identifier",
                type=openapi.TYPE_STRING,
                required=True,
                example="did:key:z2dmzD81cgPx8Vki7JbuuMmFYrWPgYoytykUZ3eyqht1j9KbsEYvdrjxMjQ4tpnje9BDBTzuNDP3knn6qLZErzd4bJ5go2CChoPjd5GAH3zpFJP5fuwSk66U5Pq6EhF4nKnHzDnznEP8fX99nZGgwbAh1o7Gj1X52Tdhf7U4KTk66xsA5r",
            ),
            openapi.Parameter(
                name="redirect_uri",
                in_=openapi.IN_QUERY,
                description="The client's redirection endpoint",
                type=openapi.TYPE_STRING,
                required=True,
                example="openid:",
            ),
            openapi.Parameter(
                name="nonce",
                in_=openapi.IN_QUERY,
                description="A random value generated by the client",
                type=openapi.TYPE_STRING,
                required=False,
                example="glkFFoisdfEui43",
            ),
            openapi.Parameter(
                name="code_challenge",
                in_=openapi.IN_QUERY,
                description="A challenge generated from the code_verifier",
                type=openapi.TYPE_STRING,
                required=False,
                example="YjI0ZTQ4NTBhMzJmMmZhNjZkZDFkYzVhNzlhNGMyZDdjZDlkMTM4YTY4NjcyMTA5M2Q2OWQ3YjNjOGJlZDBlMS AgLQo=",
            ),
            openapi.Parameter(
                name="code_challenge_method",
                in_=openapi.IN_QUERY,
                description="The method used to generate the code_challenge",
                type=openapi.TYPE_STRING,
                required=False,
                example="S256",
            ),
            openapi.Parameter(
                name="authorization_details",
                in_=openapi.IN_QUERY,
                description="The authorization details",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="client_metadata",
                in_=openapi.IN_QUERY,
                description="The client metadata",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        operation_description="GET Authorize",
        responses={302: openapi.Response("", AuthorizeResponseSerializer)},
    )
    @action(detail=False, methods=["get"], url_path="auth/authorize")
    def authorize(self, request):
        authorize = OpenidService.authorize(request)
        code = authorize.get("status_code")
        content = authorize.get("content")

        if code == 302 or code == 200:
            return Response(
                headers={
                    "Location": AuthorizeResponseSerializer(content).data[
                        "location"
                    ]
                },
                status=status.HTTP_302_FOUND,
            )

        return Response(
            headers={"Location": (content)},
            status=code,
        )

    @swagger_auto_schema(
        method="post",
        request_body=CreatedDirectPostSerializer,
        operation_description="POST Direct_post",
        responses={302: openapi.Response("", AuthorizeResponseSerializer)},
    )
    @action(detail=False, methods=["post"], url_path="auth/direct_post")
    def direct_post(self, request):
        request_data = request.data

        vp_token_present = request_data.get("vp_token") is not None
        id_token_present = request_data.get("id_token") is not None
        presentation_submission_required = (
            vp_token_present
            and request_data.get("presentation_submission") is None
        )

        if not vp_token_present and not id_token_present:
            return HttpResponseBadRequest(
                "Either vp_token or id_token must be present."
            )
        elif vp_token_present and id_token_present:
            return HttpResponseBadRequest(
                "Both vp_token and id_token can't be present at the same time."
            )
        elif presentation_submission_required:
            return HttpResponseBadRequest(
                "presentation_submission is required."
            )

        direct_post = OpenidService.direct_post(request_data)
        code = direct_post.get("status_code")
        content = direct_post.get("content")
        if code == 302 or code == 200:
            return Response(
                headers={
                    "Location": AuthorizeResponseSerializer(content).data[
                        "location"
                    ]
                },
                status=status.HTTP_302_FOUND,
            )

        return Response(
            headers={"Location": (content)},
            status=code,
        )

    @swagger_auto_schema(
        method="post",
        request_body=TokenRequestSerializer,
        operation_description="POST Token",
        responses={200: openapi.Response("", TokenResponseSerializer)},
    )
    @action(detail=False, methods=["post"], url_path="auth/token")
    def token_request(self, request):
        request_data = request.data
        if request_data.get("grant_type") is None:
            return HttpResponseBadRequest("Grant_type is required.")
        if request_data.get("grant_type") == "authorization_code":
            if request_data.get("code") is None:
                return HttpResponseBadRequest("Code is required.")
        elif (
            request_data.get("grant_type")
            == "urn:ietf:params:oauth:grant-type:pre-authorized_code"
        ):
            if request_data.get("pre-authorized_code") is None:
                return HttpResponseBadRequest(
                    "Pre-authorized_code is required."
                )
        else:
            return HttpResponseBadRequest("Grant_type error.")
        token = OpenidService.token_request(request_data)
        code = token.get("status_code")
        content = token.get("content")
        if code == 200:
            return Response(
                TokenResponseSerializer(content).data,
                status=code,
            )

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Issuer Identifier",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "code",
                openapi.IN_PATH,
                description="Preauth Code",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="GET Preauth token validation",
        responses={
            200: openapi.Response(
                "",
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="auth/token/(?P<code>\w+)")
    def exchange_preauth(self, request, code: str):
        exchange_preauth = OpenidService.exchange_preauth(settings.DID, code)
        code = exchange_preauth.get("status_code")
        content = exchange_preauth.get("content")

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="get",
        operation_description="GET Public Jwk",
        responses={200: openapi.Response("", PublicJwkSerializer)},
    )
    @action(detail=False, methods=["get"], url_path="auth/jwks")
    def get_public_jwk(self, request):

        public_jwk = OpenidService.get_public_jwk_by_issuer()
        if public_jwk:
            return Response((public_jwk))

        return HttpResponseBadRequest("Public jwk not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "data",
                openapi.IN_QUERY,
                description="Claims data",
                required=True,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="GET Claims Verification",
        responses={200: openapi.Response("", ClaimsVerificationSerializer)},
    )
    @action(
        detail=False, methods=["get"], url_path="verifier/claims-validation"
    )
    def get_claims_validation(self, request, pk: str):
        validation_result = OpenidService.get_claims_validation(request)
        if validation_result:
            return Response((validation_result))

        return HttpResponseNotFound("Verifier not found.")


class PresentationDefinitionView(RetrieveModelMixin, GenericViewSet):
    model_class = PresentationDefinition
    queryset = PresentationDefinition.objects.all()
    serializer_class = PresentationDefinitionSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def retrieve(self, request, pk: str):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class NonceManagerView(ModelViewSet):
    model_class = NonceManager
    queryset = NonceManager.objects.all()
    serializer_class = NonceManagerSerializer


class ScopeActionView(ViewSet):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend]

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "credential_types",
                openapi.IN_QUERY,
                description="Credential Type",
                required=True,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="VC Scope action",
        responses={200: openapi.Response("", VCScopeActionSerializer)},
    )
    @action(detail=False, methods=["get"], url_path="vc-scope-action")
    def vc_scope_action(self, request):
        query_credential = request.GET.get("credential_types")
        query_issuer = settings.DID
        if not query_issuer or not query_credential:
            return HttpResponseBadRequest(
                "Issuer and Credential_types queries are required"
            )
        vc_scope_action = VCScopeAction.objects.filter(
            credential_types=query_credential,
            entity=query_issuer,
        ).first()
        if vc_scope_action:
            return Response(VCScopeActionSerializer(vc_scope_action).data)

        return HttpResponseNotFound("VC Scope Action not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "scope",
                openapi.IN_QUERY,
                description="Scope",
                required=True,
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="VP Scope action",
        responses={200: openapi.Response("", VPScopeActionSerializer)},
    )
    @action(detail=False, methods=["get"], url_path="vp-scope-action")
    def vp_scope_action(self, request):
        query_scope = request.GET.get("scope")
        query_verifier = settings.DID
        if not query_verifier or not query_scope:
            return HttpResponseBadRequest(
                "Verifier and Scope queries are required"
            )
        vp_scope_action = VPScopeAction.objects.filter(
            scope=query_scope,
            entity=query_verifier,
        ).first()
        if vp_scope_action:
            return Response(VPScopeActionSerializer(vp_scope_action).data)

        return HttpResponseNotFound("VP Scope Action not found.")
