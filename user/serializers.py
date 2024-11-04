from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name"]


class CustomTokenLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user_id"] = user.id
        token["username"] = user.username
        token["email"] = user.email

        return token

    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenLoginSerializer, self).validate(attrs)
        # Custom data you want to include
        data.update({"user_id": self.user.id})
        data.update({"username": self.user.username})
        data.update({"email": self.user.email})

        return data
