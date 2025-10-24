from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification
)
from .serializers import (
    InformationSerializer, CompetenceSerializer, EducationSerializer, ExperienceSerializer,
    ProjectSerializer, MessageSerializer, ProjectInquirySerializer, InquiryMessageSerializer,
    TaskSerializer, InvoiceSerializer, InvoiceItemSerializer, DocumentSerializer,
    TeamMemberSerializer, NotificationSerializer
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
    """Create a new project inquiry"""
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

