from rest_framework.routers import SimpleRouter

from .views import OrganizationKeysView

router = SimpleRouter()
router.register(r"", OrganizationKeysView, "Organizations Keys")
urlpatterns = router.urls
