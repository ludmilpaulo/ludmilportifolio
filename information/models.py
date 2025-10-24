from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import re
import uuid
from django_ckeditor_5.fields import CKEditor5Field


class Information(models.Model):
    name_complete = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True, null=True)
    mini_about = CKEditor5Field("Text", config_name="extends")
    about = CKEditor5Field("Text", config_name="extends")
    born_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    cv = models.FileField(upload_to='cv', blank=True, null=True)

    # Social Network
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name_complete


class Competence(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    percentage = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.FileField(upload_to='competence/', blank=False, null=False)

    def __str__(self):
        return self.title


class Education(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    description = CKEditor5Field("Text", config_name="extends")
    the_year = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.title


class Experience(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    stack = models.ManyToManyField(Competence, related_name='stack',blank=True)
    company = models.CharField(max_length=50, blank=False, null=False)
    logo = models.ImageField(upload_to="logo/", blank=True, null=True)
    description = CKEditor5Field("Text", config_name="extends")
    the_year = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.title


class Project(models.Model):
    clone = 1
    live = 2
    upcoming = 3
    in_progress = 4

    STATUS_CHOICES = (
        (clone, "clone"),
        (live, "live"),
        (upcoming, "upcoming"),
        (in_progress, "in_progress"),
    )

    title = models.CharField(max_length=200, blank=False, null=False)
    slug = models.SlugField(max_length=200, blank=True, null=True)
    description = CKEditor5Field("Text", config_name="extends")
    image = models.ImageField(upload_to="projects/", blank=False, null=False)
    tools = models.ManyToManyField(Competence, related_name='tools',max_length=200, blank=False)
    demo = models.URLField()
    github = models.URLField()
    status = models.IntegerField(choices=STATUS_CHOICES, verbose_name='stado')
    show_in_slider = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_project_absolute_url(self):
        return "/projects/{}".format(self.slug)

    def save(self, *args, **kwargs):
        self.slug = self.slug_generate()
        super(Project, self).save(*args, **kwargs)

    def slug_generate(self):
        slug = self.title.strip()
        slug = re.sub(" ", "_", slug)
        return slug.lower()


class Message(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=255, null=False, blank=False)
    message = models.TextField(null=False, blank=False)
    send_time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# New models for dashboard functionality
class ProjectInquiry(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in-progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]
    
    WEB_APP = 'web-app'
    MOBILE_APP = 'mobile-app'
    E_COMMERCE = 'e-commerce'
    DESKTOP_APP = 'desktop-app'
    OTHER = 'other'
    
    PROJECT_TYPE_CHOICES = [
        (WEB_APP, 'Web Application'),
        (MOBILE_APP, 'Mobile Application'),
        (E_COMMERCE, 'E-commerce'),
        (DESKTOP_APP, 'Desktop Application'),
        (OTHER, 'Other'),
    ]

    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    project_title = models.CharField(max_length=200)
    project_description = models.TextField()
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default=WEB_APP)
    budget = models.CharField(max_length=100)
    timeline = models.CharField(max_length=100)
    additional_requirements = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    
    # Project tracking fields
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    progress = models.IntegerField(default=0)  # 0-100 percentage
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_name} - {self.project_title}"


class InquiryMessage(models.Model):
    CLIENT = 'client'
    ADMIN = 'admin'
    
    SENDER_CHOICES = [
        (CLIENT, 'Client'),
        (ADMIN, 'Admin'),
    ]

    inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.inquiry.project_title}"


class Task(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in-progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]

    inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    assigned_to = models.CharField(max_length=50, default='admin')  # 'admin' or 'client'
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.inquiry.project_title}"


class Invoice(models.Model):
    SENT = 'sent'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (SENT, 'Sent'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
        (CANCELLED, 'Cancelled'),
    ]

    inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SENT)
    due_date = models.DateTimeField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.inquiry.project_title}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"


class Document(models.Model):
    CONTRACT = 'contract'
    NDA = 'nda'
    AGREEMENT = 'agreement'
    PROPOSAL = 'proposal'
    OTHER = 'other'
    
    TYPE_CHOICES = [
        (CONTRACT, 'Contract'),
        (NDA, 'NDA'),
        (AGREEMENT, 'Agreement'),
        (PROPOSAL, 'Proposal'),
        (OTHER, 'Other'),
    ]
    
    DRAFT = 'draft'
    PENDING_SIGNATURE = 'pending-signature'
    SIGNED = 'signed'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING_SIGNATURE, 'Pending Signature'),
        (SIGNED, 'Signed'),
        (EXPIRED, 'Expired'),
    ]

    inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    download_url = models.URLField()
    signed_at = models.DateTimeField(blank=True, null=True)
    signed_by = models.CharField(max_length=100, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.inquiry.project_title}"


class TeamMember(models.Model):
    inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.role}"


class Notification(models.Model):
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    
    TYPE_CHOICES = [
        (INFO, 'Info'),
        (SUCCESS, 'Success'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
    ]
    
    INQUIRY = 'inquiry'
    TASK = 'task'
    DOCUMENT = 'document'
    INVOICE = 'invoice'
    GENERAL = 'general'
    
    CATEGORY_CHOICES = [
        (INQUIRY, 'Inquiry'),
        (TASK, 'Task'),
        (DOCUMENT, 'Document'),
        (INVOICE, 'Invoice'),
        (GENERAL, 'General'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=INFO)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=GENERAL)
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.type}"


# User Authentication Models
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('client', 'Client'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class ClientAccount(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_account')
    project_inquiry = models.ForeignKey(ProjectInquiry, on_delete=models.CASCADE, related_name='client_accounts')
    auto_generated = models.BooleanField(default=True)
    credentials_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Client account for {self.user.username}"