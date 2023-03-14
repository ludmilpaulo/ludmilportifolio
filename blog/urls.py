from django.urls import path, include
from rest_framework import routers
from .api.views import CourseViewSet, SubjectListView, SubjectDetailView
from . import views

router = routers.DefaultRouter()
router.register('blogs', CourseViewSet)

app_name = "blog"
urlpatterns = [
    path('subjects/',
         SubjectListView.as_view(),
         name='subject_list'),
    path('subjects/<pk>/',
         SubjectDetailView.as_view(),
         name='subject_detail'),

    path('', include(router.urls)),
    
    path('mine/',
         views.ManageCourseListView.as_view(),
         name='manage_course_list'),

    path('create/',
         views.CourseCreateView.as_view(),
         name='course_create'),

    path('<pk>/edit/',
         views.CourseUpdateView.as_view(),
         name='course_edit'),

    path('<pk>/delete/',
         views.CourseDeleteView.as_view(),
         name='course_delete'),

    path('<pk>/module/',
     views.CourseModuleUpdateView.as_view(),
     name='course_module_update'),

    path('module/<int:module_id>/content/<model_name>/create/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_create'),

    path('module/<int:module_id>/content/<model_name>/<id>/',
         views.ContentCreateUpdateView.as_view(),
         name='module_content_update'),

    path('content/<int:id>/delete/',
         views.ContentDeleteView.as_view(),
         name='module_content_delete'),

    path('module/<int:module_id>/',
         views.ModuleContentListView.as_view(),
         name='module_content_list'),

    path('module/order/',
         views.ModuleOrderView.as_view(),
         name='module_order'),

    path('content/order/',
         views.ContentOrderView.as_view(),
         name='content_order'),

    path('subject/<slug:subject>/',
         views.CourseListView.as_view(),
         name='course_list_subject'),

    path('<slug:slug>/',
         views.CourseDetailView.as_view(),
         name='course_detail'),
]
