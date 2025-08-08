from django.contrib import admin
from .models import Employee

# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'role', 'hire_date', 'is_active']
    list_filter = ['department', 'role', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__username']
    ordering = ['employee_id']
