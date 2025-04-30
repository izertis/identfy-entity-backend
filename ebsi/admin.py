from django.contrib import admin

from ebsi.enums import AccreditationTypes
from ebsi.forms import AttestationForm, OnboardingForm
from ebsi.models import (
    AccreditationToAccredit,
    AccreditationToAttest,
    AccreditationToOnboard,
    EbsiAccreditation,
    PotentialAccreditationInformation,
)


# Register your models here.
class EbsiAccreditationAdmin(admin.ModelAdmin):
    model = (EbsiAccreditation,)
    readonly_fields = ("type",)
    list_display = ["type"]


class PotentialAccreditationInformationAdmin(admin.ModelAdmin):
    model = (PotentialAccreditationInformation,)
    list_display = ("type", "attribute_id")
    readonly_fields = (
        "type",
        "accredited_for",
        "accredited_schema",
        "attribute_id",
    )
    inlines = []


class AccreditationToAttestAdmin(admin.ModelAdmin):
    form = AttestationForm

    list_display = ["did"]

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        form.type = AccreditationTypes.VerifiableAccreditationToAttest.value
        return form

    def save_model(self, request, obj, form, change):
        obj.type = AccreditationTypes.VerifiableAccreditationToAttest.value
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(
            type=AccreditationTypes.VerifiableAccreditationToAttest.value
        )


class AccreditationToAccreditAdmin(admin.ModelAdmin):
    form = AttestationForm

    list_display = ["did"]

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        form.type = AccreditationTypes.VerifiableAccreditationToAccredit.value
        return form

    def save_model(self, request, obj, form, change):
        obj.type = AccreditationTypes.VerifiableAccreditationToAccredit.value
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(
            type=AccreditationTypes.VerifiableAccreditationToAccredit.value
        )


class AccreditationToOnboardAdmin(admin.ModelAdmin):
    form = OnboardingForm

    list_display = ["did"]

    def get_form(self, request, obj, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        form.type = AccreditationTypes.VerifiableAuthorisationToOnboard.value
        form.base_fields["schema"].label = "Terms of use"
        return form

    def save_model(self, request, obj, form, change):
        obj.type = AccreditationTypes.VerifiableAuthorisationToOnboard.value
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(
            type=AccreditationTypes.VerifiableAuthorisationToOnboard.value
        )


admin.site.register(EbsiAccreditation, EbsiAccreditationAdmin)
admin.site.register(
    PotentialAccreditationInformation, PotentialAccreditationInformationAdmin
)
admin.site.register(AccreditationToAttest, AccreditationToAttestAdmin)
admin.site.register(AccreditationToAccredit, AccreditationToAccreditAdmin)
admin.site.register(AccreditationToOnboard, AccreditationToOnboardAdmin)
