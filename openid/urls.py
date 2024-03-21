from rest_framework.routers import SimpleRouter

from .views import (
    NonceManagerView,
    OpenidView,
    PresentationDefinitionView,
    ScopeActionView,
)

router = SimpleRouter(trailing_slash=False)

router.register(r"", OpenidView, "Openid")
router.register(
    r"presentation-definition",
    PresentationDefinitionView,
    "PresentationDefinition",
)
router.register(r"nonce-manager", NonceManagerView, "NonceManager")
router.register(r"", ScopeActionView, "ScopeAction")
urlpatterns = router.urls
