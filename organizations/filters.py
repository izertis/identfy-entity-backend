from django_filters import rest_framework as filters

from organizations.models import OrganizationKeys


class OrganizationKeysFilters(filters.FilterSet):
    type = filters.CharFilter(field_name="type", method="filter_type_not_none")

    def filter_name_not_none(self, queryset, value):
        if value == "":
            return queryset.none()
        return queryset.filter(name__exact=value)

    def filter_type_not_none(self, queryset, type, value):
        if value == "":
            return queryset.none()
        return queryset.filter(type__exact=value).order_by("type").distinct()

    class Meta:
        model = OrganizationKeys
        fields = [
            "type",
        ]
