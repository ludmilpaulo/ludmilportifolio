from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InformationViewSet, CompetenceViewSet, EducationViewSet, ExperienceViewSet,
    ProjectViewSet, MessageViewSet, ProjectInquiryViewSet, InquiryMessageViewSet,
    TaskViewSet, InvoiceViewSet, InvoiceItemViewSet, DocumentViewSet,
    TeamMemberViewSet, NotificationViewSet, submit_message, my_info,
    create_project_inquiry, get_project_inquiries, add_task, update_task_status,
    add_document, sign_document, add_team_member, update_project_progress,
    add_message, create_invoice, get_notifications, update_notification
)

router = DefaultRouter()
router.register(r'information', InformationViewSet)
router.register(r'competence', CompetenceViewSet)
router.register(r'education', EducationViewSet)
router.register(r'experience', ExperienceViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'project-inquiries', ProjectInquiryViewSet)
router.register(r'inquiry-messages', InquiryMessageViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'team-members', TeamMemberViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('submit-message/', submit_message, name='submit_message'),
    path('my-info/', my_info, name='my_info'),
    
    # Dashboard API endpoints
    path('create-project-inquiry/', create_project_inquiry, name='create_project_inquiry'),
    path('get-project-inquiries/', get_project_inquiries, name='get_project_inquiries'),
    path('add-task/', add_task, name='add_task'),
    path('update-task-status/', update_task_status, name='update_task_status'),
    path('add-document/', add_document, name='add_document'),
    path('sign-document/', sign_document, name='sign_document'),
    path('add-team-member/', add_team_member, name='add_team_member'),
    path('update-project-progress/', update_project_progress, name='update_project_progress'),
    path('add-message/', add_message, name='add_message'),
    path('create-invoice/', create_invoice, name='create_invoice'),
    path('get-notifications/', get_notifications, name='get_notifications'),
    path('update-notification/', update_notification, name='update_notification'),
]
