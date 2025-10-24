from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PasswordResetToken, UserProfile, LoginLog, ClientAccount


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'company', 'is_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website')
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'login_time', 'logout_time', 'is_successful')
    list_filter = ('is_successful', 'login_time')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('login_time',)


@admin.register(ClientAccount)
class ClientAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'project_inquiry_id', 'auto_generated', 'credentials_sent', 'created_at')
    list_filter = ('auto_generated', 'credentials_sent', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
