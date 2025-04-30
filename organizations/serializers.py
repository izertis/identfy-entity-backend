from rest_framework import serializers

from .models import OrganizationKeys


class OrganizationKeysSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationKeys
        fields = "__all__"


class DidResponseSerializer(serializers.Serializer):
    did = serializers.CharField(max_length=255, required=True)
    mail_box_private_key = serializers.CharField(max_length=255, required=False)
    mail_box_public_key = serializers.CharField(max_length=255, required=False)
