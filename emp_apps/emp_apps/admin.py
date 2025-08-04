from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, AttendanceRecord, AttendanceSettings, LeaveRequest


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user_full_name', 'employee_id', 'department', 'position', 'is_active', 'hire_date']
    list_filter = ['department', 'position', 'is_active', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'department']
    list_editable = ['is_active']
    ordering = ['user__first_name', 'user__last_name']
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Full Name'
    user_full_name.admin_order_field = 'user__first_name'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'date', 'check_in_display', 'check_out_display', 'work_hours', 'status_display']
    list_filter = ['status', 'date', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    date_hierarchy = 'date'
    ordering = ['-date', '-check_in_time']
    readonly_fields = ['work_hours', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'date')
        }),
        ('Time Records', {
            'fields': ('check_in_time', 'check_out_time', 'work_hours')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.user.get_full_name() or obj.employee.user.username
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__user__first_name'
    
    def check_in_display(self, obj):
        if obj.check_in_time:
            color = 'green' if not obj.is_late() else 'orange'
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                obj.check_in_time.strftime('%H:%M:%S')
            )
        return format_html('<span style="color: red;">Not recorded</span>')
    check_in_display.short_description = 'Check In'
    
    def check_out_display(self, obj):
        if obj.check_out_time:
            return format_html(
                '<span style="color: blue;">{}</span>',
                obj.check_out_time.strftime('%H:%M:%S')
            )
        return format_html('<span style="color: red;">Not recorded</span>')
    check_out_display.short_description = 'Check Out'
    
    def status_display(self, obj):
        colors = {
            'present': 'green',
            'late': 'orange',
            'absent': 'red',
            'half_day': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'standard_check_in_time', 'standard_check_out_time', 'standard_work_hours', 'late_threshold_minutes']
    
    fieldsets = (
        ('Standard Times', {
            'fields': ('standard_check_in_time', 'standard_check_out_time', 'standard_work_hours', 'overtime_threshold')
        }),
        ('Time Restrictions', {
            'fields': (
                ('check_in_start_time', 'check_in_end_time'),
                ('check_out_start_time', 'check_out_end_time')
            ),
            'description': 'Define the allowed time windows for check-in and check-out'
        }),
        ('Grace Periods & Thresholds', {
            'fields': (
                'late_threshold_minutes',
                ('check_in_grace_minutes_before', 'check_in_grace_minutes_after'),
                ('check_out_grace_minutes_before', 'check_out_grace_minutes_after')
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings object
        return not AttendanceSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status_display', 'applied_date']
    list_filter = ['status', 'leave_type', 'applied_date', 'start_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id', 'reason']
    date_hierarchy = 'applied_date'
    ordering = ['-applied_date']
    readonly_fields = ['applied_date', 'approved_date', 'duration_days']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'duration_days', 'reason')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_date', 'admin_comments')
        }),
        ('System Information', {
            'fields': ('applied_date',),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.user.get_full_name() or obj.employee.user.username
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__user__first_name'
    
    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
