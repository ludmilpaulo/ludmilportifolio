from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone


class CustomUser(AbstractUser):
    """Custom User Model for Authentication"""
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
    
    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='customuser',
    )
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class PasswordResetToken(models.Model):
    """Password Reset Token Model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset for {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'


class UserProfile(models.Model):
    """Extended User Profile Model"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Social Media Links
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


class LoginLog(models.Model):
    """Login Activity Log Model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_successful = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Login log for {self.user.username} at {self.login_time}"
    
    class Meta:
        verbose_name = 'Login Log'
        verbose_name_plural = 'Login Logs'
        ordering = ['-login_time']


class ClientAccount(models.Model):
    """Client Account Model for Project Inquiries"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_account')
    project_inquiry_id = models.IntegerField()  # Reference to ProjectInquiry without foreign key to avoid circular imports
    auto_generated = models.BooleanField(default=True)
    credentials_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Client account for {self.user.username}"
    
    class Meta:
        verbose_name = 'Client Account'
        verbose_name_plural = 'Client Accounts'
