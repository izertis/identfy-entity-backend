from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializers import CustomTokenLoginSerializer


class LoginViewCustom(TokenObtainPairView):
    serializer_class = CustomTokenLoginSerializer
