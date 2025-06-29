from django.db import models
from django.contrib.auth.models import User

class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    id_number_or_passport = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        abstract = True

class PatientProfile(BaseProfile):
    def __str__(self):
        return f"Patient: {self.name} {self.surname}"


class ConsultationCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DoctorProfile(BaseProfile):
    specialty = models.CharField(max_length=100)
    years_of_experience = models.IntegerField(default=0)
    consultation_category = models.ForeignKey(ConsultationCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Doctor: {self.name} {self.surname} - {self.consultation_category}"

class ConcreteDoctorProfile(DoctorProfile):
    class Meta:
        verbose_name = "Concrete Doctor Profile"
        verbose_name_plural = "Concrete Doctor Profiles"






class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ManagementProfile(BaseProfile):
    position = models.CharField(max_length=100)

    def __str__(self):
        return f"Management: {self.name} {self.surname}"