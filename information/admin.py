from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Information, Competence, Education, Experience, Project, Message,
    ProjectInquiry, InquiryMessage, Task, Invoice, InvoiceItem, 
    Document, TeamMember, Notification, Certificate, Resume,
    MeetingType, AvailabilityWindow, Booking,
)

@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ('name_complete', 'email', 'phone')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "sort_order", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)
    list_editable = ("is_published", "sort_order")

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'percentage')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('title', 'the_year')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "issuer",
        "category",
        "issued_on",
        "is_published",
        "sort_order",
    )
    list_filter = ("category", "is_published")
    search_fields = ("title", "issuer", "credential_id")
    list_editable = ("is_published", "sort_order")
    readonly_fields = ("image_preview",)
    fields = (
        "title",
        "issuer",
        "category",
        "issued_on",
        "expires_on",
        "credential_id",
        "credential_url",
        "description",
        "image",
        "image_preview",
        "document",
        "sort_order",
        "is_published",
    )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:48px;width:72px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'the_year')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'show_in_slider')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "status", "show_in_slider")}),
        ("Case study", {"fields": ("problem", "role", "outcomes", "image_alt"), "description": "Shown on the public case study. Leave outcomes blank unless you can verify them. Mark featured work with “show in slider”."}),
        ("Content", {"fields": ("description", "image", "tools", "demo", "github")}),
    )

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

@admin.register(MeetingType)
class MeetingTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_minutes", "buffer_minutes", "is_active", "sort_order")
    list_editable = ("duration_minutes", "buffer_minutes", "is_active", "sort_order")
    search_fields = ("name", "name_pt", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AvailabilityWindow)
class AvailabilityWindowAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_time", "end_time", "timezone")
    list_filter = ("weekday", "timezone")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "meeting_type", "starts_at", "visitor_timezone", "status")
    list_filter = ("status", "meeting_type")
    search_fields = ("name", "email", "company")
    readonly_fields = ("token", "created_at", "updated_at", "video_url")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'category', 'is_read', 'created_at')
    list_filter = ('type', 'category', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
