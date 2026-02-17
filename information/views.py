from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
import uuid
import random
import string

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.views.decorators.http import require_http_methods

from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification
)
from accounts.models import CustomUser, PasswordResetToken, ClientAccount
from testimonials.models import Testimonial
from .serializers import (
    InformationSerializer, CompetenceSerializer, EducationSerializer, ExperienceSerializer,
    ProjectSerializer, MessageSerializer, ProjectInquirySerializer, InquiryMessageSerializer,
    TaskSerializer, InvoiceSerializer, InvoiceItemSerializer, DocumentSerializer,
    TeamMemberSerializer, NotificationSerializer, CustomUserSerializer, PasswordResetTokenSerializer,
    ClientAccountSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)


def _parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    return s in ["1", "true", "yes", "y", "on"]


def _map_project_status(value):
    """
    Project.status is an IntegerField with:
      1=clone, 2=live, 3=upcoming, 4=in_progress
    Accepts int or string labels from frontend.
    """
    if value is None:
        return Project.live
    try:
        n = int(value)
        if n in [Project.clone, Project.live, Project.upcoming, Project.in_progress]:
            return n
    except Exception:
        pass

    s = str(value).strip().lower().replace("_", "-")
    if s == "clone":
        return Project.clone
    if s == "live":
        return Project.live
    if s == "upcoming":
        return Project.upcoming
    if s in ["in-progress", "inprogress", "in progress"]:
        return Project.in_progress
    return Project.live


def _parse_tools_ids(data):
    """
    Accept tools as:
      - tools: "1,2,3"
      - tools: ["1","2"]
      - tools[] repeated fields
    """
    if hasattr(data, "getlist"):
        tools_list = data.getlist("tools") or data.getlist("tools[]")
        if tools_list:
            return [int(x) for x in tools_list if str(x).strip().isdigit()]
    raw = data.get("tools") if hasattr(data, "get") else None
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [int(x) for x in raw if str(x).strip().isdigit()]
    parts = [p.strip() for p in str(raw).split(",") if p.strip()]
    return [int(p) for p in parts if p.isdigit()]

class InformationViewSet(viewsets.ModelViewSet):
    queryset = Information.objects.all()
    serializer_class = InformationSerializer

class CompetenceViewSet(viewsets.ModelViewSet):
    queryset = Competence.objects.all()
    serializer_class = CompetenceSerializer

class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# New ViewSets for dashboard functionality
class ProjectInquiryViewSet(viewsets.ModelViewSet):
    queryset = ProjectInquiry.objects.all()
    serializer_class = ProjectInquirySerializer

class InquiryMessageViewSet(viewsets.ModelViewSet):
    queryset = InquiryMessage.objects.all()
    serializer_class = InquiryMessageSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    
def my_info(request):
    try:
        # Ensure request has proper host for URL building
        if not hasattr(request, 'META') or 'HTTP_HOST' not in request.META:
            # Set default host for production
            if not hasattr(request, 'META'):
                request.META = {}
            if 'HTTP_HOST' not in request.META:
                request.META['HTTP_HOST'] = 'ludmil.pythonanywhere.com'
            if 'wsgi.url_scheme' not in request.META:
                request.META['wsgi.url_scheme'] = 'https'
        
        competences = CompetenceSerializer(
            Competence.objects.all().order_by('id'),
            many=True,
            context={"request": request}
        ).data
        
        education = EducationSerializer(
            Education.objects.all().order_by('-id'),
            many=True,
            context={"request": request}
        ).data
        
        experiences = ExperienceSerializer(
            Experience.objects.all().order_by('-id'),
            many=True,
            context={"request": request}
        ).data
        
        projects = ProjectSerializer(
            Project.objects.filter(show_in_slider=True).order_by('-id'),
            many=True,
            context={"request": request}
        ).data
        
        info = InformationSerializer(
            Information.objects.all(),
            many=True,
            context={"request": request}
        ).data

        return JsonResponse({
            "competences": competences,
            "experiences": experiences,
            "projects": projects,
            "info": info,
            "education": education
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in my_info: {str(e)}")
        print(f"Traceback: {error_trace}")
        # Return a more user-friendly error response
        return JsonResponse({
            "error": "Internal server error",
            "message": str(e),
            "competences": [],
            "experiences": [],
            "projects": [],
            "info": [],
            "education": []
        }, status=500)


import json


@csrf_exempt
def submit_message(request):
    if request.method == 'POST':
        try:
            # Load JSON data from request body
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message_content = data.get('message')
            print(f"Received name: {name}, email: {email}, message: {message_content}")


            # Check if all required fields are present
            if not all([name, email, message_content]):
                return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

            # Save the message in the database
            message = Message.objects.create(
                name=name,
                email=email,
                message=message_content
            )

            # Send a confirmation email to the user
            send_mail(
                'Message Received',
                'Thank you for your message. We will be in touch soon.',
                'support@maindodigital.com',  # From email
                [email],  # To email
                fail_silently=False,
            )

            return JsonResponse({'success': True, 'message': 'Message received and confirmation email sent.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


# Dashboard API endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def create_project_inquiry(request):
    """Create a new project inquiry and auto-create client account"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.create(
            client_name=data.get('clientName'),
            client_email=data.get('clientEmail'),
            client_phone=data.get('clientPhone', ''),
            project_title=data.get('projectTitle'),
            project_description=data.get('projectDescription'),
            project_type=data.get('projectType', 'web-app'),
            budget=data.get('budget', ''),
            timeline=data.get('timeline', ''),
            additional_requirements=data.get('additionalRequirements', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium')
        )
        
        # Auto-create client account
        username, password = generate_client_credentials()
        
        # Check if user already exists
        if CustomUser.objects.filter(email=data.get('clientEmail')).exists():
            user = CustomUser.objects.get(email=data.get('clientEmail'))
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=data.get('clientEmail'),
                password=password,
                first_name=data.get('clientName', '').split(' ')[0],
                last_name=' '.join(data.get('clientName', '').split(' ')[1:]) if len(data.get('clientName', '').split(' ')) > 1 else '',
                user_type='client',
                phone=data.get('clientPhone', ''),
                is_verified=True
            )
        
        # Create client account link
        client_account, created = ClientAccount.objects.get_or_create(
            user=user,
            project_inquiry_id=inquiry.id,
            defaults={'auto_generated': True}
        )
        
        # Send credentials email if new account
        if created:
            send_mail(
                'Your Client Portal Access',
                f'''
                Dear {data.get('clientName')},
                
                Thank you for your project inquiry: {data.get('projectTitle')}
                
                Your client portal access has been created:
                Username: {username}
                Password: {password}
                
                You can access your portal at: {settings.FRONTEND_URL}/client-login
                
                Best regards,
                Ludmil Paulo
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [data.get('clientEmail')],
                fail_silently=True,  # Don't fail inquiry creation if email fails (e.g. local dev)
            )
            client_account.credentials_sent = True
            client_account.save()
        
        # Create notification
        Notification.objects.create(
            title='New Project Inquiry',
            message=f'{inquiry.client_name} submitted a new project inquiry: {inquiry.project_title}',
            type='info',
            category='inquiry',
            action_url='/dashboard/client',
            action_text='View Inquiry'
        )
        
        serializer = ProjectInquirySerializer(inquiry)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_projects(request):
    """Return ALL portfolio projects for admin dashboard (not just slider)."""
    projects = Project.objects.all().order_by('-id')
    serializer = ProjectSerializer(projects, many=True, context={"request": request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_project(request):
    """Create a portfolio project (supports multipart upload for image)."""
    try:
        data = request.data
        title = data.get('title')
        description = data.get('description', '')
        demo = data.get('demo') or data.get('url') or ''
        github = data.get('github') or data.get('githubUrl') or ''
        show_in_slider = _parse_bool(data.get('showInSlider') or data.get('show_in_slider'), default=False)
        status_value = _map_project_status(data.get('status'))
        tools_ids = _parse_tools_ids(data)

        image = None
        if hasattr(request, 'FILES'):
            image = request.FILES.get('image')

        if not title:
            return Response({'success': False, 'error': 'title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not demo:
            return Response({'success': False, 'error': 'demo/url is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not github:
            return Response({'success': False, 'error': 'github/githubUrl is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not image:
            return Response({'success': False, 'error': 'image file is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not tools_ids:
            return Response({'success': False, 'error': 'at least one tool is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(
            title=title,
            description=description,
            demo=demo,
            github=github,
            status=status_value,
            show_in_slider=show_in_slider,
            image=image,
        )
        project.tools.set(Competence.objects.filter(id__in=tools_ids))
        project.save()

        serializer = ProjectSerializer(project, context={"request": request})
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_project(request):
    """Update a portfolio project (supports multipart upload for image)."""
    try:
        data = request.data
        project_id = data.get('id') or data.get('projectId')
        if not project_id:
            return Response({'success': False, 'error': 'id/projectId is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.get(id=int(project_id))

        # Update fields if provided
        if data.get('title') is not None:
            project.title = data.get('title')
        if data.get('description') is not None:
            project.description = data.get('description')
        if data.get('demo') is not None or data.get('url') is not None:
            project.demo = data.get('demo') or data.get('url') or project.demo
        if data.get('github') is not None or data.get('githubUrl') is not None:
            project.github = data.get('github') or data.get('githubUrl') or project.github
        if data.get('status') is not None:
            project.status = _map_project_status(data.get('status'))
        if data.get('showInSlider') is not None or data.get('show_in_slider') is not None:
            project.show_in_slider = _parse_bool(data.get('showInSlider') or data.get('show_in_slider'), default=project.show_in_slider)

        # Image (optional)
        if hasattr(request, 'FILES') and request.FILES.get('image'):
            project.image = request.FILES.get('image')

        # Tools (optional)
        tools_ids = _parse_tools_ids(data)
        if tools_ids:
            project.tools.set(Competence.objects.filter(id__in=tools_ids))

        project.save()

        serializer = ProjectSerializer(project, context={"request": request})
        return Response({'success': True, 'data': serializer.data})
    except Project.DoesNotExist:
        return Response({'success': False, 'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_project(request):
    """Delete a portfolio project."""
    try:
        data = request.data
        project_id = data.get('id') or data.get('projectId')
        if not project_id:
            return Response({'success': False, 'error': 'id/projectId is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.get(id=int(project_id))
        project.delete()
        return Response({'success': True})
    except Project.DoesNotExist:
        return Response({'success': False, 'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_inquiries(request):
    """Get all project inquiries"""
    inquiries = ProjectInquiry.objects.all().order_by('-created_at')
    serializer = ProjectInquirySerializer(inquiries, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([AllowAny])
def update_inquiry(request):
    """Update a project inquiry"""
    try:
        data = request.data
        inquiry_id = data.get('id') or data.get('inquiryId')
        if not inquiry_id:
            return Response({'success': False, 'error': 'id/inquiryId is required'}, status=status.HTTP_400_BAD_REQUEST)

        inquiry = ProjectInquiry.objects.get(id=int(inquiry_id))

        # Update fields if provided
        if data.get('clientName') is not None:
            inquiry.client_name = data.get('clientName')
        if data.get('clientEmail') is not None:
            inquiry.client_email = data.get('clientEmail')
        if data.get('clientPhone') is not None:
            inquiry.client_phone = data.get('clientPhone')
        if data.get('projectTitle') is not None:
            inquiry.project_title = data.get('projectTitle')
        if data.get('projectDescription') is not None:
            inquiry.project_description = data.get('projectDescription')
        if data.get('projectType') is not None:
            inquiry.project_type = data.get('projectType')
        if data.get('budget') is not None:
            inquiry.budget = data.get('budget')
        if data.get('timeline') is not None:
            inquiry.timeline = data.get('timeline')
        if data.get('additionalRequirements') is not None:
            inquiry.additional_requirements = data.get('additionalRequirements')
        if data.get('status') is not None:
            inquiry.status = data.get('status')
        if data.get('priority') is not None:
            inquiry.priority = data.get('priority')
        if data.get('estimatedCost') is not None:
            inquiry.estimated_cost = data.get('estimatedCost')
        if data.get('actualCost') is not None:
            inquiry.actual_cost = data.get('actualCost')
        if data.get('progress') is not None:
            inquiry.progress = data.get('progress')

        inquiry.save()

        serializer = ProjectInquirySerializer(inquiry)
        return Response({'success': True, 'data': serializer.data})
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_inquiry(request):
    """Delete a project inquiry"""
    try:
        data = request.data
        inquiry_id = data.get('id') or data.get('inquiryId')
        if not inquiry_id:
            return Response({'success': False, 'error': 'id/inquiryId is required'}, status=status.HTTP_400_BAD_REQUEST)

        inquiry = ProjectInquiry.objects.get(id=int(inquiry_id))
        inquiry.delete()
        return Response({'success': True})
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_task(request):
    """Add a task to a project inquiry"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        task = Task.objects.create(
            inquiry=inquiry,
            title=data.get('title'),
            description=data.get('description'),
            assigned_to=data.get('assignedTo', 'admin'),
            due_date=data.get('dueDate'),
            priority=data.get('priority', 'medium')
        )
        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_task_status(request):
    """Update task status"""
    try:
        data = request.data
        task = Task.objects.get(id=data.get('taskId'))
        task.status = data.get('status')
        task.save()
        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data})
    except Task.DoesNotExist:
        return Response({'success': False, 'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_document(request):
    """Add a document to a project inquiry (supports file upload and rich text content)"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        expires_at = None
        raw_expires = data.get('expiresAt') or data.get('expires_at')
        if raw_expires:
            try:
                # Accept ISO string
                expires_at = timezone.datetime.fromisoformat(str(raw_expires).replace('Z', '+00:00'))
            except Exception:
                expires_at = None
        
        # Handle file upload
        uploaded_file = request.FILES.get('file')
        download_url = data.get('downloadUrl') or ''
        
        # If file is uploaded, generate download URL from the file
        if uploaded_file:
            # The file will be saved automatically by Django's FileField
            # We'll set download_url after saving
            pass
        
        document = Document.objects.create(
            inquiry=inquiry,
            title=data.get('title'),
            type=data.get('type'),
            download_url=download_url,
            content=data.get('content', ''),
            status=data.get('status') or Document.PENDING_ADMIN_SIGNATURE,
            expires_at=expires_at,
        )
        
        # Save file if uploaded
        if uploaded_file:
            document.file = uploaded_file
            # Generate download URL from the file
            if hasattr(document.file, 'url'):
                document.download_url = request.build_absolute_uri(document.file.url)
            document.save()
        
        serializer = DocumentSerializer(document)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_document(request):
    """Sign a document (admin signs first, then client)."""
    try:
        data = request.data
        document = Document.objects.get(id=data.get('documentId'))
        signer_role = (data.get('signerRole') or data.get('role') or '').strip().lower()
        signed_by = data.get('signedBy') or 'Unknown'

        if signer_role == 'admin':
            document.admin_signed_at = timezone.now()
            document.admin_signed_by = signed_by
            # Move to client signature step
            document.status = Document.PENDING_CLIENT_SIGNATURE
            document.save()

            # Notify client to sign
            try:
                frontend = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
                sign_link = f"{frontend}/dashboard/client" if frontend else ""
                send_mail(
                    f"Please sign: {document.title}",
                    (
                        f"Hello {document.inquiry.client_name},\n\n"
                        f"The admin has signed the document \"{document.title}\" and is requesting your signature.\n\n"
                        f"Document type: {document.type}\n"
                        f"Access your client dashboard to sign: {sign_link}\n\n"
                        f"Thank you."
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [document.inquiry.client_email],
                    fail_silently=True,
                )
            except Exception:
                pass

        elif signer_role == 'client':
            document.client_signed_at = timezone.now()
            document.client_signed_by = signed_by

            # If admin already signed, we can finalize as signed
            if document.admin_signed_at:
                document.status = Document.SIGNED
                # Populate legacy fields for older frontend code
                document.signed_at = document.client_signed_at
                document.signed_by = document.client_signed_by
            else:
                # Client signed first (unusual) - require admin signature next
                document.status = Document.PENDING_ADMIN_SIGNATURE
            document.save()
        else:
            return Response({'success': False, 'error': 'signerRole must be admin or client'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DocumentSerializer(document)
        return Response({'success': True, 'data': serializer.data})
    except Document.DoesNotExist:
        return Response({'success': False, 'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_team_member(request):
    """Add a team member to a project inquiry"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        team_member = TeamMember.objects.create(
            inquiry=inquiry,
            name=data.get('name'),
            role=data.get('role'),
            email=data.get('email')
        )
        serializer = TeamMemberSerializer(team_member)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_project_progress(request):
    """Update project progress"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        inquiry.progress = data.get('progress', inquiry.progress)
        inquiry.actual_cost = data.get('actualCost', inquiry.actual_cost)
        inquiry.save()
        serializer = ProjectInquirySerializer(inquiry)
        return Response({'success': True, 'data': serializer.data})
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_message(request):
    """Add a message to a project inquiry"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        message = InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=data.get('sender'),
            message=data.get('message')
        )
        serializer = InquiryMessageSerializer(message)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_invoice(request):
    """Create an invoice for a project inquiry and notify client"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        
        # Parse due_date if it's a string
        due_date = data.get('dueDate')
        if isinstance(due_date, str):
            try:
                from django.utils.dateparse import parse_datetime
                due_date = parse_datetime(due_date) or timezone.now() + timezone.timedelta(days=30)
            except Exception:
                due_date = timezone.now() + timezone.timedelta(days=30)
        elif not due_date:
            due_date = timezone.now() + timezone.timedelta(days=30)
        
        invoice = Invoice.objects.create(
            inquiry=inquiry,
            invoice_number=data.get('invoiceNumber'),
            amount=data.get('amount'),
            due_date=due_date,
            description=data.get('description', ''),
            status=data.get('status', Invoice.SENT)
        )
        
        # Add invoice items if provided
        items_data = data.get('items', [])
        total_from_items = 0
        for item_data in items_data:
            qty = item_data.get('quantity', 1)
            price = item_data.get('price', 0)
            total_from_items += qty * price
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item_data.get('description', ''),
                quantity=qty,
                price=price
            )
        
        # Create notification for client
        try:
            Notification.objects.create(
                title=f"New Invoice: {invoice.invoice_number}",
                message=f"An invoice for ${invoice.amount} has been sent for project: {inquiry.project_title}",
                type=Notification.INFO,
                category=Notification.INVOICE,
                action_url=f"/dashboard/client",
                action_text="View Invoice"
            )
        except Exception:
            pass
        
        # Send email notification to client
        try:
            frontend = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
            invoice_link = f"{frontend}/dashboard/client" if frontend else ""
            send_mail(
                f"New Invoice: {invoice.invoice_number}",
                (
                    f"Hello {inquiry.client_name},\n\n"
                    f"A new invoice has been issued for your project: {inquiry.project_title}\n\n"
                    f"Invoice Number: {invoice.invoice_number}\n"
                    f"Amount: ${invoice.amount}\n"
                    f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}\n"
                    f"Description: {invoice.description}\n\n"
                    f"View and pay your invoice: {invoice_link}\n\n"
                    f"Thank you."
                ),
                settings.DEFAULT_FROM_EMAIL,
                [inquiry.client_email],
                fail_silently=True,
            )
        except Exception:
            pass
        
        serializer = InvoiceSerializer(invoice)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_invoice_status(request):
    """Update invoice status (paid/unpaid/sent/overdue/cancelled)"""
    try:
        data = request.data
        invoice_id = data.get('id') or data.get('invoiceId')
        if not invoice_id:
            return Response({'success': False, 'error': 'id/invoiceId is required'}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.get(id=int(invoice_id))
        new_status = data.get('status')
        
        if new_status not in [Invoice.SENT, Invoice.PAID, Invoice.OVERDUE, Invoice.CANCELLED]:
            return Response({'success': False, 'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = invoice.status
        invoice.status = new_status
        invoice.save()

        # Create notification if status changed to paid
        if new_status == Invoice.PAID and old_status != Invoice.PAID:
            try:
                Notification.objects.create(
                    title=f"Invoice Paid: {invoice.invoice_number}",
                    message=f"Invoice {invoice.invoice_number} has been marked as paid.",
                    type=Notification.SUCCESS,
                    category=Notification.INVOICE,
                    action_url=f"/dashboard/inquiries",
                    action_text="View Invoice"
                )
            except Exception:
                pass

        serializer = InvoiceSerializer(invoice)
        return Response({'success': True, 'data': serializer.data})
    except Invoice.DoesNotExist:
        return Response({'success': False, 'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_notifications(request):
    """Get all notifications"""
    notifications = Notification.objects.all().order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([AllowAny])
def update_notification(request):
    """Update notification status"""
    try:
        data = request.data
        notification = Notification.objects.get(id=data.get('id'))
        notification.is_read = data.get('isRead', notification.is_read)
        notification.save()
        serializer = NotificationSerializer(notification)
        return Response({'success': True, 'data': serializer.data})
    except Notification.DoesNotExist:
        return Response({'success': False, 'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_analytics(request):
    """Get analytics data for dashboard"""
    try:
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Calculate date ranges
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        last_60_days = now - timedelta(days=60)
        
        # Get total counts
        total_projects = Project.objects.count()
        total_testimonials = Testimonial.objects.count()
        total_inquiries = ProjectInquiry.objects.count()
        total_tasks = Task.objects.count()
        
        # Get recent activity
        if hasattr(Project, 'created_at'):
            recent_projects = Project.objects.filter(created_at__gte=last_30_days).count()
            old_projects = Project.objects.filter(
                created_at__lt=last_30_days,
                created_at__gte=last_60_days
            ).count()
        else:
            recent_projects = 0
            old_projects = 0
        recent_inquiries = ProjectInquiry.objects.filter(created_at__gte=last_30_days).count()
        recent_tasks = Task.objects.filter(created_at__gte=last_30_days).count()
        
        # Calculate changes
        projects_change = ((recent_projects - old_projects) / old_projects * 100) if old_projects > 0 else 0
        
        old_inquiries = ProjectInquiry.objects.filter(created_at__lt=last_30_days, created_at__gte=last_60_days).count()
        inquiries_change = ((recent_inquiries - old_inquiries) / old_inquiries * 100) if old_inquiries > 0 else 0
        
        # Project inquiries by status
        pending_inquiries = ProjectInquiry.objects.filter(status='pending').count()
        in_progress_inquiries = ProjectInquiry.objects.filter(status='in-progress').count()
        completed_inquiries = ProjectInquiry.objects.filter(status='completed').count()
        
        # Tasks by status
        pending_tasks = Task.objects.filter(status='pending').count()
        in_progress_tasks = Task.objects.filter(status='in-progress').count()
        completed_tasks = Task.objects.filter(status='completed').count()
        
        # Recent activities
        recent_activities = []
        for inquiry in ProjectInquiry.objects.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'inquiry',
                'title': f'New inquiry: {inquiry.project_title}',
                'time': inquiry.created_at.isoformat(),
                'message': f'{inquiry.client_name} submitted a new project inquiry'
            })
        
        for notification in Notification.objects.order_by('-created_at')[:5]:
            recent_activities.append({
                'type': 'notification',
                'title': notification.title,
                'time': notification.created_at.isoformat(),
                'message': notification.message
            })
        
        analytics_data = {
            'totalViews': 15420,
            'uniqueVisitors': 8930,
            'projects': total_projects,
            'testimonials': total_testimonials,
            'viewsChange': 12.5,
            'visitorsChange': 8.3,
            'projectsChange': round(projects_change, 1),
            'testimonialsChange': round(inquiries_change, 1),
            'inquiries': {
                'total': total_inquiries,
                'pending': pending_inquiries,
                'inProgress': in_progress_inquiries,
                'completed': completed_inquiries
            },
            'tasks': {
                'total': total_tasks,
                'pending': pending_tasks,
                'inProgress': in_progress_tasks,
                'completed': completed_tasks
            },
            'recentActivities': recent_activities[:10]
        }
        
        return Response({'success': True, 'data': analytics_data})
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """User login with token authentication"""
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = CustomUserSerializer(user)
                return Response({
                    'success': True,
                    'token': token.key,
                    'user': user_serializer.data
                })
            else:
                return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Send password reset email"""
    try:
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = CustomUser.objects.get(email=email)
                
                # Create password reset token
                expires_at = timezone.now() + timezone.timedelta(hours=24)
                reset_token = PasswordResetToken.objects.create(
                    user=user,
                    expires_at=expires_at
                )
                
                # Send email
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({'success': True, 'message': 'Password reset email sent'})
            except CustomUser.DoesNotExist:
                return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token"""
    try:
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
                
                if reset_token.is_expired():
                    return Response({'success': False, 'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Update password
                user = reset_token.user
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                return Response({'success': True, 'message': 'Password reset successfully'})
            except PasswordResetToken.DoesNotExist:
                return Response({'success': False, 'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def generate_client_credentials():
    """Generate random username and password for client"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return username, password

