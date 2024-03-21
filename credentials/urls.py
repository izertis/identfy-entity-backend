from rest_framework.routers import SimpleRouter

from .views import CredentialsView

router = SimpleRouter()

router.register(r"", CredentialsView, "Credentials")
urlpatterns = router.urls
