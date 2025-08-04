"""
URL configuration for emp_apps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('', views.employee_login, name='employee_login'),
    path('login/', views.employee_login, name='employee_login'),
    path('logout/', views.employee_logout, name='employee_logout'),
    
    # Main application URLs
    # CUSTOMIZATION NOTE: After login, users go to 'dashboard' (attendance functionality)
    path('dashboard/', views.attendance_dashboard, name='attendance_dashboard'),  # Main attendance page
    path('profile/', views.employee_profile, name='employee_profile'),  # Employee profile page
    path('history/', views.attendance_history, name='attendance_history'),
    
    # AJAX endpoints for check-in/out
    path('api/check-in/', views.check_in, name='check_in'),
    path('api/check-out/', views.check_out, name='check_out'),
    path('api/status/', views.get_attendance_status, name='get_attendance_status'),
    
    # Employee leave requests
    path('api/submit-leave/', views.submit_leave_request, name='submit_leave_request'),
    path('leave-requests/', views.employee_leave_requests, name='employee_leave_requests'),
    
    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('api/admin/attendance/', views.admin_get_attendance, name='admin_get_attendance'),
    path('api/admin/add-employee/', views.admin_add_employee, name='admin_add_employee'),
    path('api/admin/update-leave-status/', views.admin_update_leave_status, name='admin_update_leave_status'),
    path('api/admin/leave-details/<int:leave_id>/', views.admin_get_leave_details, name='admin_get_leave_details'),
    path('api/admin/export-attendance/', views.export_attendance_excel, name='export_attendance_excel'),
]
