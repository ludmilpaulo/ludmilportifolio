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

from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification
)
from accounts.models import CustomUser, PasswordResetToken, ClientAccount
from .serializers import (
    InformationSerializer, CompetenceSerializer, EducationSerializer, ExperienceSerializer,
    ProjectSerializer, MessageSerializer, ProjectInquirySerializer, InquiryMessageSerializer,
    TaskSerializer, InvoiceSerializer, InvoiceItemSerializer, DocumentSerializer,
    TeamMemberSerializer, NotificationSerializer, CustomUserSerializer, PasswordResetTokenSerializer,
    ClientAccountSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)

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
                fail_silently=False,
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
def get_project_inquiries(request):
    """Get all project inquiries"""
    inquiries = ProjectInquiry.objects.all().order_by('-created_at')
    serializer = ProjectInquirySerializer(inquiries, many=True)
    return Response({'success': True, 'data': serializer.data})


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
    """Add a document to a project inquiry"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        document = Document.objects.create(
            inquiry=inquiry,
            title=data.get('title'),
            type=data.get('type'),
            download_url=data.get('downloadUrl')
        )
        serializer = DocumentSerializer(document)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_document(request):
    """Sign a document"""
    try:
        data = request.data
        document = Document.objects.get(id=data.get('documentId'))
        document.status = 'signed'
        document.signed_at = timezone.now()
        document.signed_by = data.get('signedBy')
        document.save()
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
    """Create an invoice for a project inquiry"""
    try:
        data = request.data
        inquiry = ProjectInquiry.objects.get(id=data.get('inquiryId'))
        invoice = Invoice.objects.create(
            inquiry=inquiry,
            invoice_number=data.get('invoiceNumber'),
            amount=data.get('amount'),
            due_date=data.get('dueDate'),
            description=data.get('description')
        )
        
        # Add invoice items if provided
        items_data = data.get('items', [])
        for item_data in items_data:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item_data.get('description'),
                quantity=item_data.get('quantity', 1),
                price=item_data.get('price')
            )
        
        serializer = InvoiceSerializer(invoice)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_201_CREATED)
    except ProjectInquiry.DoesNotExist:
        return Response({'success': False, 'error': 'Inquiry not found'}, status=status.HTTP_404_NOT_FOUND)
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

