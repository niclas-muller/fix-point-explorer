from django.contrib import admin
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path("", include("explorer.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
