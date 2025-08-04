from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    class Meta:
        db_table = 'employees'


class AttendanceRecord(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='absent')
    work_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        db_table = 'attendance_records'
        ordering = ['-date', '-check_in_time']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date} ({self.status})"
    
    def calculate_work_hours(self):
        """Calculate work hours between check-in and check-out"""
        if self.check_in_time and self.check_out_time:
            duration = self.check_out_time - self.check_in_time
            hours = duration.total_seconds() / 3600
            self.work_hours = round(hours, 2)
            return self.work_hours
        return 0
    
    def is_late(self, standard_time="09:00"):
        """Check if employee is late based on standard check-in time"""
        if self.check_in_time:
            standard_datetime = datetime.combine(
                self.check_in_time.date(), 
                time.fromisoformat(standard_time)
            )
            standard_datetime = timezone.make_aware(standard_datetime)
            return self.check_in_time > standard_datetime
        return False
    
    def save(self, *args, **kwargs):
        # Auto-calculate work hours if both times are available
        if self.check_in_time and self.check_out_time:
            self.calculate_work_hours()
            
        # Auto-set status based on check-in time
        if self.check_in_time and self.status == 'absent':
            if self.is_late():
                self.status = 'late'
            else:
                self.status = 'present'
                
        super().save(*args, **kwargs)


class AttendanceSettings(models.Model):
    """Global settings for attendance system"""
    standard_check_in_time = models.TimeField(default=time(9, 0))  # 9:00 AM
    standard_check_out_time = models.TimeField(default=time(17, 0))  # 5:00 PM
    late_threshold_minutes = models.IntegerField(default=15)  # 15 minutes grace period
    standard_work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    overtime_threshold = models.DecimalField(max_digits=4, decimal_places=2, default=8.0)
    
    # Time range restrictions
    check_in_start_time = models.TimeField(default=time(7, 0))  # Earliest check-in: 7:00 AM
    check_in_end_time = models.TimeField(default=time(11, 0))   # Latest check-in: 11:00 AM
    check_out_start_time = models.TimeField(default=time(15, 0))  # Earliest check-out: 3:00 PM
    check_out_end_time = models.TimeField(default=time(20, 0))   # Latest check-out: 8:00 PM
    
    # Grace period settings
    check_in_grace_minutes_before = models.IntegerField(default=30)  # Can check in 30 min before standard time
    check_in_grace_minutes_after = models.IntegerField(default=120)  # Can check in 2 hours after standard time
    check_out_grace_minutes_before = models.IntegerField(default=120)  # Can check out 2 hours before standard time
    check_out_grace_minutes_after = models.IntegerField(default=180)  # Can check out 3 hours after standard time
    
    class Meta:
        db_table = 'attendance_settings'
    
    def __str__(self):
        return f"Attendance Settings - {self.standard_check_in_time} to {self.standard_check_out_time}"
    
    def is_check_in_allowed(self, current_time):
        """Check if check-in is allowed at the current time"""
        current_time_only = current_time.time()
        return self.check_in_start_time <= current_time_only <= self.check_in_end_time
    
    def is_check_out_allowed(self, current_time):
        """Check if check-out is allowed at the current time"""
        current_time_only = current_time.time()
        return self.check_out_start_time <= current_time_only <= self.check_out_end_time
    
    def get_check_in_window_message(self):
        """Get message describing the check-in time window"""
        return f"Check-in allowed between {self.check_in_start_time.strftime('%H:%M')} and {self.check_in_end_time.strftime('%H:%M')}"
    
    def get_check_out_window_message(self):
        """Get message describing the check-out time window"""
        return f"Check-out allowed between {self.check_out_start_time.strftime('%H:%M')} and {self.check_out_end_time.strftime('%H:%M')}"


class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_date = models.DateTimeField(null=True, blank=True)
    admin_comments = models.TextField(blank=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def duration_days(self):
        """Calculate the number of days for this leave request"""
        return (self.end_date - self.start_date).days + 1
