from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .settings import BACKEND_DOMAIN


def f_403(request, exception):
    return render(request, "403.html", {})


def f_404(request, exception):
    return render(request, "404.html", {})


def f_500(request):
    return render(request, "500.html", {})


handler403 = f_403
handler404 = f_404
handler500 = f_500

admin.site.site_header = "Identfy"
admin.site.index_title = "Identfy"
admin.site.site_title = "Identfy"


schema_view = get_schema_view(
    openapi.Info(
        title="Identfy API",
        default_version="v1",
        description="This api is Identfy",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    url=BACKEND_DOMAIN,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", include("credentials.urls")),
    path("", include("openid.urls")),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
    path("admin/", admin.site.urls),
    path("", lambda x: redirect("admin/")),
]
