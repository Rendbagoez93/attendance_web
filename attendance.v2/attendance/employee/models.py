from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('hr', 'HR/Admin'),
        ('staff', 'Staff'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('hr', 'Human Resources'),
        ('it', 'Information Technology'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('marketing', 'Marketing'),
        ('operations', 'Operations'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.employee_id}"
    
    class Meta:
        ordering = ['employee_id']
