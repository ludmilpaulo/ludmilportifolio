from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap


from information.views import (
    homePage,
    projectsPage,
    projectDetail,
    search,
    handler404,
)

from django.conf import settings
from django.conf.urls.static import static



from django.contrib.sitemaps.views import sitemap



handler404 = handler404

urlpatterns = [

    path('', homePage, name='homePage'),
    path('projects/', projectsPage, name='projectsPage'),
    path('projects/<str:slug>/', projectDetail, name='projectDetail'),
    path('search/', search, name='search'),

    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls),

    path('blog/', include('blog.urls', namespace='blog')),




] 


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
