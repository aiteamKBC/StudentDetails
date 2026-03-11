from django.db import models
from django.utils import timezone


def current_local_time():
    return timezone.localtime().time().replace(microsecond=0)


class AttendanceQR(models.Model):
    name = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    time = models.TimeField(default=current_local_time)

    class Meta:
        db_table = 'attendance_QR'

    def __str__(self):
        return f"{self.name} - {self.email}"


class AlternativeEmail(models.Model):
    student_id = models.BigIntegerField(primary_key=True, db_column='ID')
    aptem_name = models.CharField(max_length=255, blank=True, default='', db_column='FullName')
    group = models.CharField(max_length=255, blank=True, default='')
    attendance_group = models.CharField(max_length=255, blank=True, default='', db_column='other_group')
    attendance_reason = models.TextField(blank=True, default='', db_column='other_group_reason')
    aptem_email = models.EmailField(max_length=255, db_column='Email')
    nickname = models.CharField(max_length=255)
    alternative_email = models.EmailField(max_length=255)
    alternative_email_2 = models.EmailField(max_length=255, blank=True, default='', db_column='alternative_email_2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_alternative_details'

    def __str__(self):
        return f"{self.aptem_email} -> {self.alternative_email}"
