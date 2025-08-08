from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from employee.models import Employee
from .models import Attendance
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from datetime import time, date
import json

# Create your views here.

def user_login(request):
    """Login view with role-based redirection"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'emp_attd/login.html')

def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    """Main dashboard that redirects based on user role"""
    try:
        employee = Employee.objects.get(user=request.user)
        role = employee.role
        
        if role == 'manager':
            return redirect('manager_dashboard')
        elif role == 'hr':
            return redirect('hr_dashboard')
        elif role == 'staff':
            return redirect('employee_dashboard')
        else:
            messages.error(request, 'Unknown role. Please contact administrator.')
            return redirect('login')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact administrator.')
        return redirect('login')

@login_required
def manager_dashboard(request):
    """Manager dashboard view"""
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.role != 'manager':
            return HttpResponseForbidden("Access denied. Manager access required.")
        
        # Get all employees for manager overview
        all_employees = Employee.objects.all().order_by('employee_id')
        staff_count = Employee.objects.filter(role='staff').count()
        hr_count = Employee.objects.filter(role='hr').count()
        
        # Get today's attendance data
        today = timezone.localtime().date()
        today_attendance = Attendance.objects.filter(date=today)
        present_count = today_attendance.filter(status__in=['present', 'late']).count()
        late_count = today_attendance.filter(is_late=True).count()
        
        # Get employee's own attendance
        employee_attendance = None
        try:
            employee_attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            employee_attendance = None
        
        context = {
            'employee': employee,
            'all_employees': all_employees,
            'staff_count': staff_count,
            'hr_count': hr_count,
            'total_employees': all_employees.count(),
            'present_count': present_count,
            'late_count': late_count,
            'employee_attendance': employee_attendance,
            'current_time': timezone.localtime(),
        }
        return render(request, 'emp_attd/manager_dashboard.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')

@login_required
def hr_dashboard(request):
    """HR/Admin dashboard view"""
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.role != 'hr':
            return HttpResponseForbidden("Access denied. HR access required.")
        
        # Get employee statistics for HR
        all_employees = Employee.objects.all().order_by('employee_id')
        departments = Employee.objects.values_list('department', flat=True).distinct()
        
        # Department-wise employee count
        dept_stats = {}
        for dept in departments:
            dept_stats[dict(Employee.DEPARTMENT_CHOICES).get(dept, dept)] = Employee.objects.filter(department=dept).count()
        
        # Get today's attendance data
        today = timezone.localtime().date()
        today_attendance = Attendance.objects.filter(date=today)
        present_count = today_attendance.filter(status__in=['present', 'late']).count()
        late_count = today_attendance.filter(is_late=True).count()
        absent_count = all_employees.count() - present_count
        
        # Get employee's own attendance
        employee_attendance = None
        try:
            employee_attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            employee_attendance = None
        
        context = {
            'employee': employee,
            'all_employees': all_employees,
            'total_employees': all_employees.count(),
            'active_employees': Employee.objects.filter(is_active=True).count(),
            'dept_stats': dept_stats,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'employee_attendance': employee_attendance,
            'current_time': timezone.localtime(),
        }
        return render(request, 'emp_attd/hr_dashboard.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')

@login_required
def employee_dashboard(request):
    """Staff employee dashboard view"""
    try:
        employee = Employee.objects.get(user=request.user)
        if employee.role != 'staff':
            return HttpResponseForbidden("Access denied. Staff access required.")
        
        # Get employee's own information and department colleagues
        colleagues = Employee.objects.filter(
            department=employee.department
        ).exclude(user=request.user).order_by('employee_id')
        
        # Get today's attendance
        today = timezone.localtime().date()
        employee_attendance = None
        try:
            employee_attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            employee_attendance = None
        
        context = {
            'employee': employee,
            'colleagues': colleagues,
            'department_name': dict(Employee.DEPARTMENT_CHOICES).get(employee.department, employee.department),
            'employee_attendance': employee_attendance,
            'current_time': timezone.localtime(),
        }
        return render(request, 'emp_attd/employee_dashboard.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')

@login_required
def check_in(request):
    """Handle check-in functionality"""
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(user=request.user)
            today = timezone.localtime().date()
            now_time = timezone.localtime().time()
            
            # Check if within allowed check-in time (08:00 - 09:00)
            if not (time(8, 0) <= now_time <= time(9, 0)):
                return JsonResponse({
                    'success': False, 
                    'message': 'Check-in is only allowed between 08:00 - 09:00',
                    'type': 'error'
                })
            
            # Get or create today's attendance record
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
                date=today,
                defaults={
                    'check_in_time': now_time,
                    'status': 'late' if now_time > time(9, 15) else 'present',
                    'is_late': now_time > time(9, 15)
                }
            )
            
            if not created and attendance.check_in_time:
                return JsonResponse({
                    'success': False, 
                    'message': 'You have already checked in today',
                    'type': 'warning'
                })
            
            # Update if not already checked in
            if not attendance.check_in_time:
                attendance.check_in_time = now_time
                attendance.status = 'late' if now_time > time(9, 15) else 'present'
                attendance.is_late = now_time > time(9, 15)
                attendance.save()
            
            if attendance.is_late:
                return JsonResponse({
                    'success': True, 
                    'message': f'🕘 Checked in LATE at {now_time.strftime("%H:%M")}. Please be on time tomorrow.',
                    'type': 'warning',
                    'status': 'late'
                })
            else:
                return JsonResponse({
                    'success': True, 
                    'message': f'✅ Successfully checked in ON TIME at {now_time.strftime("%H:%M")}. Have a great day!',
                    'type': 'success',
                    'status': 'on_time'
                })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Employee profile not found',
                'type': 'error'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Invalid request method',
        'type': 'error'
    })

@login_required
def check_out(request):
    """Handle check-out functionality"""
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(user=request.user)
            today = timezone.localtime().date()
            now_time = timezone.localtime().time()
            
            # Check if within allowed check-out time (17:00 - 18:00)
            if not (time(17, 0) <= now_time <= time(18, 0)):
                return JsonResponse({
                    'success': False, 
                    'message': 'Check-out is only allowed between 17:00 - 18:00',
                    'type': 'error'
                })
            
            try:
                attendance = Attendance.objects.get(employee=employee, date=today)
                
                if not attendance.check_in_time:
                    return JsonResponse({
                        'success': False, 
                        'message': 'You must check in first before checking out',
                        'type': 'warning'
                    })
                
                if attendance.check_out_time:
                    return JsonResponse({
                        'success': False, 
                        'message': 'You have already checked out today',
                        'type': 'warning'
                    })
                
                attendance.check_out_time = now_time
                attendance.save()
                
                # Calculate work duration
                check_in_time = attendance.check_in_time
                work_duration = (timezone.datetime.combine(today, now_time) - 
                               timezone.datetime.combine(today, check_in_time)).total_seconds() / 3600
                
                return JsonResponse({
                    'success': True, 
                    'message': f'🏁 Successfully checked out at {now_time.strftime("%H:%M")}. You worked for {work_duration:.1f} hours today. Great job!',
                    'type': 'success',
                    'work_duration': f'{work_duration:.1f} hours'
                })
                
            except Attendance.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'message': 'No check-in record found for today',
                    'type': 'error'
                })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Employee profile not found',
                'type': 'error'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Invalid request method',
        'type': 'error'
    })
