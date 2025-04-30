import copy

from django.conf import settings
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from organizations.filters import OrganizationKeysFilters
from organizations.models import OrganizationKeys

from .serializers import OrganizationKeysSerializer


def get_render():
    if settings.DEBUG:
        return [BrowsableAPIRenderer]
    return [JSONRenderer]


class CustomDjangoModelPermission(DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


# Create your views here.
class BaseViewSet(ModelViewSet):
    permission_classes = (CustomDjangoModelPermission,)

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]

    renderer_classes = get_render()
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend]


class OrganizationKeysView(GenericViewSet):
    permission_classes = (CustomDjangoModelPermission,)
    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication,
        JWTAuthentication,
    ]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    model_class = OrganizationKeys
    serializer_class = OrganizationKeysSerializer
    filterset_class = OrganizationKeysFilters
    http_method_names = ["get"]

    def get_queryset(self):
        if (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="SERVICE").first()
        ):
            return OrganizationKeys.objects.all()
        elif self.request.user.is_anonymous:
            return OrganizationKeys.objects.none()
        return OrganizationKeys.objects.filter(organization__users=self.request.user)

    @swagger_auto_schema(
        method="get",
        manual_parameters=[
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description="Algorithm type: rsa, secp256k1, secp256r1",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        operation_description="GET Organization Keys",
        responses={
            200: openapi.Response("", OrganizationKeysSerializer),
            403: openapi.Response("You don't have permissions"),
        },
    )
    @action(detail=False, methods=["get"], url_path="organization-keys")
    def list_keys(self, request):
        query_type = request.GET.get("type")
        OrganizationKeys.objects.all()

        if query_type is not None:
            keys = OrganizationKeys.objects.filter(type=query_type)
        else:
            keys = keys = OrganizationKeys.objects.all()

        keys_into_list = []
        for list_key in keys:
            keys_into_list.append(OrganizationKeysSerializer(list_key).data)
        return JsonResponse(keys_into_list, safe=False)
