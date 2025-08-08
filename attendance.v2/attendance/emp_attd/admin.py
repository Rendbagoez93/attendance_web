from django.contrib import admin
from .models import Attendance

# Register your models here.

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in_time', 'check_out_time', 'status', 'is_late']
    list_filter = ['status', 'is_late', 'date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    date_hierarchy = 'date'
    ordering = ['-date', '-check_in_time']
