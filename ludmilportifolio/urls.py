from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from courses.views import CourseListView


from information.views import (
    homePage,
    projectsPage,
    projectDetail,
    my_info,
    search,
    handler404,
)

from django.conf import settings
from django.conf.urls.static import static

from blog.sitemaps import PostSitemap
from blog.views import PostListView, send_email
from django.contrib.sitemaps.views import sitemap


sitemaps = {
    'posts': PostSitemap,
}


handler404 = handler404

urlpatterns = [

    path('', homePage, name='homePage'),
    path('projects/', projectsPage, name='projectsPage'),
    path('projects/<str:slug>/', projectDetail, name='projectDetail'),
    path('search/', search, name='search'),

    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
  
    path('course/', include('courses.urls')),
    path('list/', CourseListView.as_view(), name='course_list'),
    path('students/', include('students.urls')),
    path('api/', include('courses.api.urls', namespace='api')),
    path('my_info/', my_info),
    path('contact_me/', send_email, name='send_email' ),


    path('blog/', include('blog.urls', namespace='blog')),

    path('chat/', include('chat.urls', namespace='chat')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')




] 


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
