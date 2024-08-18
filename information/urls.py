from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InformationViewSet,
    CompetenceViewSet,
    EducationViewSet,
    ExperienceViewSet,
    ProjectViewSet,
    MessageViewSet,
)

router = DefaultRouter()
router.register(r'information', InformationViewSet)
router.register(r'competence', CompetenceViewSet)
router.register(r'education', EducationViewSet)
router.register(r'experience', ExperienceViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
