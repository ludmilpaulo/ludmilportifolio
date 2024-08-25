from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.conf import settings

from information.views import my_info, submit_message
urlpatterns = [
    path("admin/", admin.site.urls),
    path('my_info/', my_info),
    path('submit-message/', submit_message, name='submit_message'),
    path(
        "ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"
    ),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
