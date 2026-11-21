from rest_framework import serializers
from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, Document, TeamMember, Notification,
    Certificate, Resume,
)
from accounts.models import CustomUser, PasswordResetToken, ClientAccount

class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        data["avatar"] = _absolute_file_url(request, instance.avatar)
        data["cv"] = _absolute_file_url(request, instance.cv)
        return data

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ("id", "title", "file", "sort_order", "is_published", "created_at")
        read_only_fields = ("created_at",)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["file"] = _absolute_file_url(self.context.get("request"), instance.file)
        return data

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = _absolute_file_url(self.context.get("request"), instance.image)
        return data

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


def _absolute_file_url(request, file_field):
    if not file_field:
        return None
    if request:
        try:
            return request.build_absolute_uri(file_field.url)
        except Exception:
            pass
    from django.conf import settings
    base_url = getattr(settings, "BASE_URL", "https://ludmil.pythonanywhere.com").rstrip("/")
    url = file_field.url if hasattr(file_field, "url") else str(file_field)
    if str(url).startswith("http"):
        return url
    return f"{base_url}{url}"


class CertificateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "title",
            "issuer",
            "issued_on",
            "expires_on",
            "category",
            "credential_id",
            "credential_url",
            "image",
            "document",
            "description",
            "sort_order",
            "is_published",
        )

    def get_image(self, obj):
        return _absolute_file_url(self.context.get("request"), obj.image)

    def get_document(self, obj):
        return _absolute_file_url(self.context.get("request"), obj.document)

class ExperienceSerializer(serializers.ModelSerializer):
    stack = CompetenceSerializer(many=True, read_only=True)
    stack_ids = serializers.PrimaryKeyRelatedField(
        source="stack",
        queryset=Competence.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Experience
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["logo"] = _absolute_file_url(self.context.get("request"), instance.logo)
        data.pop("stack_ids", None)
        return data

class ProjectSerializer(serializers.ModelSerializer):
    tools = CompetenceSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        # Explicitly list fields - DO NOT include created_at/updated_at as they don't exist in production DB
        fields = [
            'id', 'title', 'slug', 'description', 'image', 'tools', 
            'demo', 'github', 'status', 'show_in_slider'
        ]
        # Do NOT include created_at or updated_at in fields list
    
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
