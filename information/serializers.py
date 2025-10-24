from rest_framework import serializers
from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification
)

class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    stack = CompetenceSerializer(many=True, read_only=True)

    class Meta:
        model = Experience
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    tools = CompetenceSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


# New serializers for dashboard functionality
class InquiryMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryMessage
        fields = '__all__'


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ProjectInquirySerializer(serializers.ModelSerializer):
    messages = InquiryMessageSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    team_members = TeamMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProjectInquiry
        fields = '__all__'
