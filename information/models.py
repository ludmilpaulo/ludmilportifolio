from django.db import models
import re
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
    all = 1
    live = 2
    upcoming = 3
    in_progress = 4

    STATUS_CHOICES = (
        (all, "all"),
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