from django import forms

from ebsi.models import EbsiAccreditationWhiteList, PotentialAccreditationInformation


class PotentialAttestationDisplay(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.accredited_for}"


class PotentialOnboardingDisplay(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.attribute_id}"


class BaseForm(forms.ModelForm):
    class Meta:
        model = EbsiAccreditationWhiteList
        fields = "__all__"
        exclude = ["type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields[
                "schema"
            ].queryset = PotentialAccreditationInformation.objects.filter(
                type=self.type,
            )


class AttestationForm(BaseForm):
    schema = PotentialAttestationDisplay(
        queryset=PotentialAccreditationInformation.objects.all(),
    )


class OnboardingForm(BaseForm):
    schema = PotentialOnboardingDisplay(
        queryset=PotentialAccreditationInformation.objects.all(),
    )
