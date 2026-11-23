from zoneinfo import ZoneInfo

from django.contrib import admin, messages
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


@admin.action(description="Cancel selected meetings and email the visitor")
def cancel_selected_meetings(modeladmin, request, queryset):
    from .meeting_views import _send_cancellation, cancel_booking

    cancelled = 0
    emailed = 0
    for booking in queryset.select_related("meeting_type"):
        if cancel_booking(booking):
            cancelled += 1
            if _send_cancellation(booking):
                emailed += 1
    modeladmin.message_user(
        request,
        f"Cancelled {cancelled} meeting(s). Cancellation emails sent: {emailed}.",
        messages.SUCCESS,
    )


@admin.action(description="Resend the confirmation email")
def resend_selected_confirmations(modeladmin, request, queryset):
    from .meeting_views import _send_confirmation

    sent = 0
    skipped = 0
    for booking in queryset.select_related("meeting_type"):
        if booking.status != Booking.CONFIRMED:
            skipped += 1
            continue
        if _send_confirmation(booking):
            sent += 1
            if not booking.email_sent:
                booking.email_sent = True
                booking.save(update_fields=["email_sent", "updated_at"])
    modeladmin.message_user(
        request,
        f"Confirmation emails sent: {sent}. Skipped cancelled meetings: {skipped}.",
        messages.SUCCESS,
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "meeting_type",
        "cape_town_time",
        "visitor_timezone",
        "status",
        "email_sent",
        "video_link",
    )
    list_filter = ("status", "meeting_type")
    list_select_related = ("meeting_type",)
    search_fields = ("name", "email", "company", "notes")
    date_hierarchy = "starts_at"
    actions = (cancel_selected_meetings, resend_selected_confirmations)
    readonly_fields = (
        "token",
        "created_at",
        "updated_at",
        "video_link",
        "manage_link",
        "cape_town_time",
        "email_sent",
    )
    fieldsets = (
        ("Visitor", {"fields": ("name", "email", "company", "notes", "locale")}),
        ("Meeting", {"fields": ("meeting_type", "status", "starts_at", "ends_at", "buffer_minutes")}),
        ("Time zones", {"fields": ("cape_town_time", "visitor_timezone", "owner_timezone")}),
        ("Actions", {"fields": ("video_link", "manage_link", "email_sent")}),
        ("Record", {"fields": ("token", "created_at", "updated_at")}),
    )

    @admin.display(description="Cape Town", ordering="starts_at")
    def cape_town_time(self, obj):
        zone_name = obj.owner_timezone or "Africa/Johannesburg"
        try:
            zone = ZoneInfo(zone_name)
        except Exception:
            zone = ZoneInfo("Africa/Johannesburg")
        return obj.starts_at.astimezone(zone).strftime("%a %d %b %Y, %H:%M")

    @admin.display(description="Video call")
    def video_link(self, obj):
        if not obj.video_url:
            return "—"
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">Join the call</a>', obj.video_url)

    @admin.display(description="Visitor page")
    def manage_link(self, obj):
        from .meeting_views import _manage_url

        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">Open the visitor page</a>',
            _manage_url(obj.token),
        )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'category', 'is_read', 'created_at')
    list_filter = ('type', 'category', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
