from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets
from .models import Information, Competence, Education, Experience, Project, Message
from .serializers import (
    InformationSerializer,
    CompetenceSerializer,
    EducationSerializer,
    ExperienceSerializer,
    ProjectSerializer,
    MessageSerializer,
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

