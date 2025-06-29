from django.db import models
from accounts.models import DoctorProfile, PatientProfile, ConsultationCategory

class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(ConsultationCategory, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='scheduled')  # scheduled, cancelled, completed
    paid = models.BooleanField(default=False)  # Track whether the appointment is paid
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Appointment fee

    class Meta:
        unique_together = ('doctor', 'appointment_time')

    def __str__(self):
        return f"{self.patient} appointment with {self.doctor} at {self.appointment_time}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    record_date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.patient.user.username}'s record on {self.record_date}"

class Billing(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.user.username}'s bill for {self.service_name}"
