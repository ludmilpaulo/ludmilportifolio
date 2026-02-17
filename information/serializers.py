from rest_framework import serializers
from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification
)
from accounts.models import CustomUser, PasswordResetToken, ClientAccount

class InformationSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    cv = serializers.SerializerMethodField()
    
    class Meta:
        model = Information
        fields = '__all__'
    
    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.avatar.url)
                except Exception:
                    # Fallback to relative URL or absolute URL with settings
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
                    return f"{base_url}{obj.avatar.url}" if hasattr(obj.avatar, 'url') else str(obj.avatar)
            # Fallback when no request context
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
            return f"{base_url}{obj.avatar.url}" if hasattr(obj.avatar, 'url') else str(obj.avatar)
        return None
    
    def get_cv(self, obj):
        if obj.cv:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.cv.url)
                except Exception:
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
                    return f"{base_url}{obj.cv.url}" if hasattr(obj.cv, 'url') else str(obj.cv)
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
            return f"{base_url}{obj.cv.url}" if hasattr(obj.cv, 'url') else str(obj.cv)
        return None

class CompetenceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Competence
        fields = '__all__'
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.image.url)
                except Exception:
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
                    return f"{base_url}{obj.image.url}" if hasattr(obj.image, 'url') else str(obj.image)
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
            return f"{base_url}{obj.image.url}" if hasattr(obj.image, 'url') else str(obj.image)
        return None

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    stack = CompetenceSerializer(many=True, read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = '__all__'
    
    def get_logo(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.logo.url)
                except Exception:
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
                    return f"{base_url}{obj.logo.url}" if hasattr(obj.logo, 'url') else str(obj.logo)
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
            return f"{base_url}{obj.logo.url}" if hasattr(obj.logo, 'url') else str(obj.logo)
        return None

class ProjectSerializer(serializers.ModelSerializer):
    tools = CompetenceSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
    
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.image.url)
                except Exception:
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
                    return f"{base_url}{obj.image.url}" if hasattr(obj.image, 'url') else str(obj.image)
            from django.conf import settings
            base_url = getattr(settings, 'BASE_URL', 'https://ludmil.pythonanywhere.com')
            return f"{base_url}{obj.image.url}" if hasattr(obj.image, 'url') else str(obj.image)
        return None

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


# User Authentication Serializers
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'company', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at']


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ['token', 'created_at', 'expires_at']


class ClientAccountSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = ClientAccount
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)
