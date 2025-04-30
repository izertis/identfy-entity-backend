from rest_framework.routers import SimpleRouter

from .views import CredentialAuthView, CredentialsView

router = SimpleRouter()

router.register(r"", CredentialsView, "Credentials")
router.register(r"", CredentialAuthView, "CredentialAuth")
urlpatterns = router.urls
