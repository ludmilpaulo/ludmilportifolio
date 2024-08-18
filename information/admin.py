from django.contrib import admin
from .models import Information, Competence, Education, Experience, Project, Message

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
