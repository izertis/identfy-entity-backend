from django.contrib import admin
from django.urls import path

from credentials.admin import request_vc_from_external_issuer

original_get_urls = admin.site.get_urls()


def custom_get_urls():
    custom_urls = [
        path(
            "request-vc/",
            admin.site.admin_view(request_vc_from_external_issuer),
            name="request-vc-view",
        ),
    ]
    return custom_urls + original_get_urls


admin.site.get_urls = custom_get_urls
