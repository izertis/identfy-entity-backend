from django_filters import rest_framework as filters

from openid.models import IssuanceFlow, VerifyFlow


class IssuanceFlowFilters(filters.FilterSet):
    credential_types = filters.CharFilter(
        field_name="credential_types",
        method="filter_credential_type_not_none",
        required=True,
    )

    def filter_credential_type_not_none(self, queryset, name, value):
        if value == "":
            return IssuanceFlow.objects.none()
        return queryset.filter(credential_types__exact=value).distinct()


class VerifyFlowFilters(filters.FilterSet):
    scope = filters.CharFilter(
        field_name="scope",
        method="filter_scope_not_none",
        required=True,
    )

    def filter_scope_not_none(self, queryset, name, value):
        if value == "":
            return VerifyFlow.objects.none()
        return queryset.filter(scope__exact=value).distinct()
