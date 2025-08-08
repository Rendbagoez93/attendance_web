from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manager/', views.manager_dashboard, name='manager_dashboard'),
    path('hr/', views.hr_dashboard, name='hr_dashboard'),
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
]
