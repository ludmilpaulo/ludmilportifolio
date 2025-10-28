from django.contrib import admin
from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, 
    Document, TeamMember, Notification
)

@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ('name_complete', 'email', 'phone')

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'percentage')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('title', 'the_year')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'the_year')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'show_in_slider')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'send_time', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'message')


# Dashboard models
@admin.register(ProjectInquiry)
class ProjectInquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'project_title', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'project_type', 'created_at')
    search_fields = ('client_name', 'client_email', 'project_title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(InquiryMessage)
class InquiryMessageAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'sender', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message', 'inquiry__client_name')
    readonly_fields = ('timestamp',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'inquiry', 'status', 'assigned_to', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'assigned_to')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'inquiry', 'amount', 'status', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'inquiry__client_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [InvoiceItemInline]

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'inquiry', 'type', 'status')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('title', 'inquiry__client_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'inquiry', 'role', 'email')
    search_fields = ('name', 'email', 'role')
    readonly_fields = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'category', 'is_read', 'created_at')
    list_filter = ('type', 'category', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
