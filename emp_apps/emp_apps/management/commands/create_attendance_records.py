"""
CUSTOMIZATION NOTE: Attendance Records Creation Command
This command creates sample attendance records for all employees
Run this command: python manage.py create_attendance_records

Weekends (Saturday & Sunday) are automatically marked as holidays
Separate from employee creation for better modularity and performance
"""

from django.core.management.base import BaseCommand
from emp_apps.models import Employee, AttendanceRecord
from datetime import date, time, datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Create sample attendance records for employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            default='2025-01-01',
            help='Start date for attendance records (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            default=str(date.today()),
            help='End date for attendance records (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--employees',
            nargs='+',
            help='Specific employee IDs to create records for'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing attendance records before creating new ones'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to create in each batch'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample attendance records...')
        
        # Parse dates
        try:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
            return
        
        if start_date > end_date:
            self.stdout.write(self.style.ERROR('Start date must be before end date'))
            return
        
        # Get employees
        if options['employees']:
            employees = Employee.objects.filter(
                employee_id__in=options['employees'],
                is_active=True
            )
            if not employees.exists():
                self.stdout.write(self.style.ERROR('No matching employees found'))
                return
        else:
            employees = Employee.objects.filter(is_active=True)
        
        if not employees.exists():
            self.stdout.write(self.style.WARNING('No employees found'))
            return
        
        # Clear existing records if requested
        if options['clear_existing']:
            deleted_count = AttendanceRecord.objects.filter(
                employee__in=employees,
                date__range=[start_date, end_date]
            ).delete()[0]
            self.stdout.write(f'Cleared {deleted_count} existing records')
        
        # Create attendance records
        total_records_created = 0
        batch_size = options['batch_size']
        
        for employee in employees:
            self.stdout.write(f'Processing {employee.user.get_full_name()} ({employee.employee_id})...')
            
            records_to_create = []
            current_date = start_date
            
            while current_date <= end_date:
                # Check if record already exists (unless clearing)
                if not options['clear_existing'] and AttendanceRecord.objects.filter(
                    employee=employee, 
                    date=current_date
                ).exists():
                    current_date += timedelta(days=1)
                    continue
                
                # Generate attendance record (including weekends as holidays)
                record = self.generate_attendance_record(employee, current_date)
                if record:
                    records_to_create.append(record)
                    
                    # Create records in batches for better performance
                    if len(records_to_create) >= batch_size:
                        AttendanceRecord.objects.bulk_create(records_to_create)
                        total_records_created += len(records_to_create)
                        records_to_create = []
                
                current_date += timedelta(days=1)
            
            # Create remaining records
            if records_to_create:
                AttendanceRecord.objects.bulk_create(records_to_create)
                total_records_created += len(records_to_create)
            
            employee_total = AttendanceRecord.objects.filter(
                employee=employee,
                date__range=[start_date, end_date]
            ).count()
            self.stdout.write(f'  ✓ {employee_total} records for {employee.user.get_full_name()}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Attendance record creation completed!'
                f'\n📅 Date range: {start_date} to {end_date}'
                f'\n👥 Employees processed: {employees.count()}'
                f'\n📊 Total records created: {total_records_created}'
            )
        )

    def generate_attendance_record(self, employee, current_date):
        """Generate a realistic attendance record for the given employee and date"""
        
        # Check if it's weekend (Saturday=5, Sunday=6)
        if current_date.weekday() >= 5:
            return AttendanceRecord(
                employee=employee,
                date=current_date,
                status='holiday'
            )
        
        # Random attendance pattern for weekdays (85% present, 10% late, 5% absent)
        rand = random.random()
        
        if rand < 0.05:  # 5% absent
            return AttendanceRecord(
                employee=employee,
                date=current_date,
                status='absent'
            )
            
        elif rand < 0.15:  # 10% late
            # Late check-in (9:15 - 10:30)
            late_minutes = random.randint(15, 90)
            check_in_time = datetime.combine(current_date, time(9, 0)) + timedelta(minutes=late_minutes)
            check_in_time = timezone.make_aware(check_in_time)
            
            # Check-out time (17:00 - 18:30)
            check_out_minutes = random.randint(0, 90)
            check_out_time = datetime.combine(current_date, time(17, 0)) + timedelta(minutes=check_out_minutes)
            check_out_time = timezone.make_aware(check_out_time)
            
            # Calculate work hours
            work_duration = check_out_time - check_in_time
            work_hours = work_duration.total_seconds() / 3600
            
            return AttendanceRecord(
                employee=employee,
                date=current_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                work_hours=round(work_hours, 2),
                status='late'
            )
            
        else:  # 85% present on time
            # Normal check-in (8:45 - 9:15)
            check_in_minutes = random.randint(-15, 15)
            check_in_time = datetime.combine(current_date, time(9, 0)) + timedelta(minutes=check_in_minutes)
            check_in_time = timezone.make_aware(check_in_time)
            
            # Normal check-out (17:00 - 18:00)
            check_out_minutes = random.randint(0, 60)
            check_out_time = datetime.combine(current_date, time(17, 0)) + timedelta(minutes=check_out_minutes)
            check_out_time = timezone.make_aware(check_out_time)
            
            # Calculate work hours
            work_duration = check_out_time - check_in_time
            work_hours = work_duration.total_seconds() / 3600
            
            return AttendanceRecord(
                employee=employee,
                date=current_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                work_hours=round(work_hours, 2),
                status='present'
            )
