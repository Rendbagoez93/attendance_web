from django.db import models
from django.contrib.auth.models import User
from employee.models import Employee
from django.utils import timezone
from datetime import time

# Create your models here.

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    is_late = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', '-check_in_time']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date} - {self.status}"
    
    @property
    def can_check_in(self):
        """Check if current time allows check-in (08:00 - 09:00)"""
        now = timezone.localtime().time()
        return time(8, 0) <= now <= time(9, 0) and not self.check_in_time
    
    @property
    def can_check_out(self):
        """Check if current time allows check-out (17:00 - 18:00)"""
        now = timezone.localtime().time()
        return time(17, 0) <= now <= time(18, 0) and self.check_in_time and not self.check_out_time
    
    @property
    def is_checked_in_today(self):
        """Check if already checked in today"""
        return bool(self.check_in_time)
    
    @property
    def is_checked_out_today(self):
        """Check if already checked out today"""
        return bool(self.check_out_time)
