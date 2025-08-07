"""
CUSTOMIZATION NOTE: Sample Data Creation Command
This command creates sample employees and attendance settings for TechCorp
Run this command: python manage.py create_sample_data

For attendance records, use separate command: python manage.py create_attendance_records

You can modify the sample data below to match your company structure
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from emp_apps.models import Employee, AttendanceSettings
from datetime import date, time


class Command(BaseCommand):
    help = 'Create sample employee data for TechCorp (use create_attendance_records for attendance data)'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for TechCorp...')
        
        # Create attendance settings if they don't exist
        settings, created = AttendanceSettings.objects.get_or_create(
            pk=1,
            defaults={
                'standard_check_in_time': time(9, 0),  # 9:00 AM
                'standard_check_out_time': time(17, 0),  # 5:00 PM
                'check_in_start_time': time(7, 0),  # 7:00 AM
                'check_in_end_time': time(11, 0),   # 11:00 AM
                'check_out_start_time': time(15, 0),  # 3:00 PM
                'check_out_end_time': time(20, 0),   # 8:00 PM
                'late_threshold_minutes': 15,
                'standard_work_hours': 8.0,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Attendance settings created'))
        else:
            self.stdout.write('✓ Attendance settings already exist')

        # Sample employee data for TechCorp
        # CUSTOMIZATION NOTE: Modify this data to match your company departments and positions
        sample_employees = [
            {
                'username': 'john.doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@techcorp.com',
                'employee_id': 'TC001',
                'department': 'Software Development',
                'position': 'Senior Developer',
                'phone_number': '+1-555-0101',
            },
            {
                'username': 'jane.smith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@techcorp.com',
                'employee_id': 'TC002',
                'department': 'Human Resources',
                'position': 'HR Manager',
                'phone_number': '+1-555-0102',
            },
            {
                'username': 'mike.wilson',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'email': 'mike.wilson@techcorp.com',
                'employee_id': 'TC003',
                'department': 'Marketing',
                'position': 'Marketing Specialist',
                'phone_number': '+1-555-0103',
            },
            {
                'username': 'sarah.davis',
                'first_name': 'Sarah',
                'last_name': 'Davis',
                'email': 'sarah.davis@techcorp.com',
                'employee_id': 'TC004',
                'department': 'Finance',
                'position': 'Financial Analyst',
                'phone_number': '+1-555-0104',
            },
            {
                'username': 'alex.brown',
                'first_name': 'Alex',
                'last_name': 'Brown',
                'email': 'alex.brown@techcorp.com',
                'employee_id': 'TC005',
                'department': 'Software Development',
                'position': 'Junior Developer',
                'phone_number': '+1-555-0105',
            }
        ]

        created_count = 0
        for emp_data in sample_employees:
            # Create user if doesn't exist
            user, user_created = User.objects.get_or_create(
                username=emp_data['username'],
                defaults={
                    'first_name': emp_data['first_name'],
                    'last_name': emp_data['last_name'],
                    'email': emp_data['email'],
                }
            )
            
            if user_created:
                user.set_password('employee123')  # Default password
                user.save()
            
            # Create employee profile if doesn't exist
            employee, emp_created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': emp_data['employee_id'],
                    'department': emp_data['department'],
                    'position': emp_data['position'],
                    'phone_number': emp_data['phone_number'],
                    'hire_date': date(2023, 1, 15),  # Sample hire date
                    'is_active': True,
                }
            )
            
            if emp_created:
                created_count += 1
                self.stdout.write(f'✓ Created employee: {emp_data["first_name"]} {emp_data["last_name"]} ({emp_data["employee_id"]})')
            else:
                self.stdout.write(f'✓ Employee already exists: {emp_data["first_name"]} {emp_data["last_name"]}')

        # Create an employee profile for the existing admin user if it doesn't exist
        try:
            admin_user = User.objects.get(username='admin')
            admin_employee, created = Employee.objects.get_or_create(
                user=admin_user,
                defaults={
                    'employee_id': 'TC000',
                    'department': 'Administration',
                    'position': 'System Administrator',
                    'phone_number': '+1-555-0100',
                    'hire_date': date(2023, 1, 1),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('✓ Created admin employee profile'))
            else:
                self.stdout.write('✓ Admin employee profile already exists')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('! Admin user not found - create superuser first'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Employee data creation completed!'
                f'\n📊 Created {created_count} new employees'
                f'\n🏢 Company: TechCorp Solutions'
                f'\n🔐 Default password for all employees: employee123'
                f'\n\n📝 CUSTOMIZATION NOTES:'
                f'\n   - Modify employee data in this command file'
                f'\n   - Update company name in templates'
                f'\n   - Change default passwords for security'
                f'\n   - Add more departments/positions as needed'
                f'\n\n📅 To create attendance records, run:'
                f'\n   python manage.py create_attendance_records'
            )
        )


