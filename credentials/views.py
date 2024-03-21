from django.http.response import HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from credentials.service import CredentialService

from .serializers import (
    CredentialResponseSerializer,
    DeferredRegistry,
    EbsiCredentialRequestSerializer,
    ExternalDataResponse,
)


# Create your views here.
class CredentialsView(ViewSet):
    permission_classes = (AllowAny,)
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    @swagger_auto_schema(
        method="post",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Auth Token",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        request_body=EbsiCredentialRequestSerializer,
        operation_description="POST Credentials",
        responses={200: openapi.Response("", CredentialResponseSerializer)},
    )
    @action(detail=False, methods=["post"], url_path="credentials")
    def credentials(self, request):
        credentials = CredentialService.credentials(
            request, request.headers.get("Authorization")
        )
        code = credentials.get("status_code")
        content = credentials.get("content")

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="post",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Auth Token",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        operation_description="POST Deferred Credentials",
        responses={200: openapi.Response("", CredentialResponseSerializer)},
    )
    @action(detail=False, methods=["post"], url_path="credential_deferred")
    def deferred_credentials(self, request):
        deferred_credentials = CredentialService.deferred_credentials(
            request.headers.get("Authorization")
        )
        if deferred_credentials:
            return Response(
                CredentialResponseSerializer(deferred_credentials).data
            )

        return HttpResponseBadRequest("Credentials not found.")

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "vc_type",
                openapi.IN_QUERY,
                description="Credential Schema Name",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="User identifier",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "pin",
                openapi.IN_QUERY,
                description="User identifier",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        operation_description="GET Credential External Data",
        responses={200: openapi.Response("", ExternalDataResponse)},
    )
    @action(detail=False, methods=["get"], url_path="credentials/external-data")
    def external_data_credentials(self, request):
        external_data = CredentialService.external_data(
            request.GET.get("vc_type"),
            request.GET.get("user_id"),
            request.GET.get("pin"),
        )
        code = external_data.get("status_code")
        content = external_data.get("content")

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="post",
        request_body=DeferredRegistry,
        operation_description="POST Registry Deferred token",
        responses={
            200: openapi.Response(
                "",
            )
        },
    )
    @action(detail=False, methods=["post"], url_path="deferred/register")
    def register_deferred(self, request):
        register_deferred = CredentialService.register_deferred(request)
        code = register_deferred.get("status_code")
        content = register_deferred.get("content")

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "code",
                openapi.IN_PATH,
                description="Deferred Code",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="GET Deferred token validation",
        responses={
            200: openapi.Response(
                "",
            )
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="deferred/exchange/(?P<code>\w+)",
    )
    def exchange_deferred(self, code: str):
        exchange_deferred = CredentialService.exchange_deferred(code)
        code = exchange_deferred.get("status_code")
        content = exchange_deferred.get("content")

        return Response(
            content,
            status=code,
        )
