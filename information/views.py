from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
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
