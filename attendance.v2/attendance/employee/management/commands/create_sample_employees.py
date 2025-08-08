from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from datetime import date, datetime
import random

class Command(BaseCommand):
    help = 'Create sample employee data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample employee data...'))
        
        # Sample data
        employees_data = [
            {
                'username': 'john.smith',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@company.com',
                'employee_id': 'EMP001',
                'phone_number': '+1234567890',
                'address': '123 Main St, New York, NY',
                'department': 'operations',
                'role': 'manager',
                'hire_date': date(2020, 1, 15),
                'salary': 75000.00
            },
            {
                'username': 'sarah.johnson',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah.johnson@company.com',
                'employee_id': 'EMP002',
                'phone_number': '+1234567891',
                'address': '456 Oak Ave, Los Angeles, CA',
                'department': 'hr',
                'role': 'hr',
                'hire_date': date(2020, 3, 10),
                'salary': 65000.00
            },
            {
                'username': 'mike.davis',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'email': 'mike.davis@company.com',
                'employee_id': 'EMP003',
                'phone_number': '+1234567892',
                'address': '789 Pine St, Chicago, IL',
                'department': 'it',
                'role': 'staff',
                'hire_date': date(2021, 2, 20),
                'salary': 55000.00
            },
            {
                'username': 'lisa.wilson',
                'first_name': 'Lisa',
                'last_name': 'Wilson',
                'email': 'lisa.wilson@company.com',
                'employee_id': 'EMP004',
                'phone_number': '+1234567893',
                'address': '321 Elm St, Houston, TX',
                'department': 'finance',
                'role': 'staff',
                'hire_date': date(2021, 5, 12),
                'salary': 52000.00
            },
            {
                'username': 'david.brown',
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david.brown@company.com',
                'employee_id': 'EMP005',
                'phone_number': '+1234567894',
                'address': '654 Maple Ave, Phoenix, AZ',
                'department': 'sales',
                'role': 'staff',
                'hire_date': date(2021, 8, 5),
                'salary': 48000.00
            },
            {
                'username': 'jennifer.miller',
                'first_name': 'Jennifer',
                'last_name': 'Miller',
                'email': 'jennifer.miller@company.com',
                'employee_id': 'EMP006',
                'phone_number': '+1234567895',
                'address': '987 Cedar St, Philadelphia, PA',
                'department': 'marketing',
                'role': 'staff',
                'hire_date': date(2022, 1, 18),
                'salary': 50000.00
            },
            {
                'username': 'robert.garcia',
                'first_name': 'Robert',
                'last_name': 'Garcia',
                'email': 'robert.garcia@company.com',
                'employee_id': 'EMP007',
                'phone_number': '+1234567896',
                'address': '147 Birch Ln, San Antonio, TX',
                'department': 'it',
                'role': 'staff',
                'hire_date': date(2022, 4, 25),
                'salary': 53000.00
            },
            {
                'username': 'emily.martinez',
                'first_name': 'Emily',
                'last_name': 'Martinez',
                'email': 'emily.martinez@company.com',
                'employee_id': 'EMP008',
                'phone_number': '+1234567897',
                'address': '258 Spruce St, San Diego, CA',
                'department': 'finance',
                'role': 'staff',
                'hire_date': date(2022, 7, 8),
                'salary': 51000.00
            },
            {
                'username': 'james.anderson',
                'first_name': 'James',
                'last_name': 'Anderson',
                'email': 'james.anderson@company.com',
                'employee_id': 'EMP009',
                'phone_number': '+1234567898',
                'address': '369 Willow Dr, Dallas, TX',
                'department': 'sales',
                'role': 'staff',
                'hire_date': date(2023, 2, 14),
                'salary': 49000.00
            },
            {
                'username': 'michelle.taylor',
                'first_name': 'Michelle',
                'last_name': 'Taylor',
                'email': 'michelle.taylor@company.com',
                'employee_id': 'EMP010',
                'phone_number': '+1234567899',
                'address': '741 Poplar St, San Jose, CA',
                'department': 'marketing',
                'role': 'staff',
                'hire_date': date(2023, 6, 30),
                'salary': 47000.00
            }
        ]
        
        # Clear existing data
        Employee.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create employees
        for emp_data in employees_data:
            # Create user
            user = User.objects.create_user(
                username=emp_data['username'],
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                email=emp_data['email'],
                password='password123'  # Default password
            )
            
            # Create employee
            Employee.objects.create(
                user=user,
                employee_id=emp_data['employee_id'],
                phone_number=emp_data['phone_number'],
                address=emp_data['address'],
                department=emp_data['department'],
                role=emp_data['role'],
                hire_date=emp_data['hire_date'],
                salary=emp_data['salary']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created employee: {emp_data["first_name"]} {emp_data["last_name"]} ({emp_data["role"]})')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created 10 employees: 1 Manager, 1 HR/Admin, 8 Staff')
        )
