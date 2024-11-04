from typing import Any

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest, HttpResponseNotFound
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from credentials.models import IssuedVerifiableCredential, StatusList2021
from credentials.service import CredentialService

from .serializers import (
    ChangeStatus,
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
    def credentials(
        self,
        request,
    ):
        credentials = CredentialService.credentials(
            request,
            request.headers.get("Authorization"),
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
    def deferred_credentials(
        self,
        request,
    ):
        deferred_credentials = CredentialService.deferred_credentials(
            request.headers.get("Authorization"),
        )
        if deferred_credentials:
            return Response(CredentialResponseSerializer(deferred_credentials).data)

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
        register_deferred = CredentialService.register_deferred(request.data)
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
        detail=False, methods=["get"], url_path="deferred/exchange/(?P<code>[^/.]+)"
    )
    def exchange_deferred(self, request, code: str):
        exchange_deferred = CredentialService.exchange_deferred(code)
        code = exchange_deferred.get("status_code")
        content = exchange_deferred.get("content")

        return Response(
            content,
            status=code,
        )

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "list_id",
                openapi.IN_PATH,
                description="VC Identifier",
                type=openapi.TYPE_STRING,
            ),
        ],
        operation_description="GET VC Status",
        responses={
            200: openapi.Response(
                "",
            )
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="credentials/status/list/(?P<list_id>[\w-]+)",
    )
    def credential_status(self, request, list_id: str):
        status_list = StatusList2021.objects.filter(
            id=list_id,
        ).first()
        if not status_list:
            return HttpResponseNotFound("Status list " + list_id + " not found")
        result = CredentialService.issue_status_credential(status_list)
        code = result.get("status_code")
        content = result.get("content")

        return HttpResponse(content, status=code, content_type="text/plain")


class CredentialAuthView(ViewSet):
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = (IsAuthenticated,)
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    @swagger_auto_schema(
        method="put",
        manual_parameters=[
            openapi.Parameter(
                "vc_id",
                openapi.IN_PATH,
                description="VC Identifier",
                type=openapi.TYPE_STRING,
            ),
        ],
        request_body=ChangeStatus,
        operation_description="Put Issued Credential Status",
        responses={
            200: openapi.Response(
                "",
            )
        },
    )
    @action(
        detail=False,
        methods=["put"],
        url_path="credentials/(?P<vc_id>[\w-]+)/status",
    )
    def change_credential_status(self, request: Any, vc_id: str):
        vc = IssuedVerifiableCredential.objects.filter(
            vc_id=vc_id,
        ).first()

        if not vc:
            return HttpResponseNotFound("Required VC " + vc_id + " not found")
        result = CredentialService.change_credential_status(vc, request.data)
        code = result.get("status_code")
        message = result.get("message")

        return Response(
            message,
            status=code,
        )
