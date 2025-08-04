from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from emp_apps.models import Employee, LeaveRequest
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample leave requests for testing'
    
    def handle(self, *args, **options):
        """Create sample leave requests"""
        
        # Get all employees
        employees = Employee.objects.all()
        
        if not employees.exists():
            self.stdout.write(
                self.style.ERROR('No employees found. Please create employees first using create_sample_data.')
            )
            return
        
        # Leave types to choose from
        leave_types = ['sick', 'vacation', 'personal', 'emergency']
        statuses = ['pending', 'approved', 'rejected']
        
        # Sample reasons for each leave type
        reasons = {
            'sick': [
                'Flu symptoms and fever',
                'Doctor appointment for routine checkup',
                'Recovery from minor surgery',
                'Migraine headache',
                'Food poisoning'
            ],
            'vacation': [
                'Family vacation to beach resort',
                'Wedding anniversary celebration',
                'Visiting relatives in another city',
                'Personal holiday and rest',
                'Honeymoon trip'
            ],
            'personal': [
                'Personal family matters',
                'House moving and relocation',
                'Attending family function',
                'Personal errands and appointments',
                'Child care arrangements'
            ],
            'emergency': [
                'Family emergency',
                'Medical emergency of family member',
                'Urgent personal matter',
                'Home emergency repair',
                'Unexpected situation'
            ]
        }
        
        # Create 20 sample leave requests
        leave_requests_created = 0
        
        for i in range(20):
            employee = random.choice(employees)
            leave_type = random.choice(leave_types)
            
            # Random dates
            start_date = date.today() + timedelta(days=random.randint(-30, 60))
            duration = random.randint(1, 7)  # 1 to 7 days
            end_date = start_date + timedelta(days=duration - 1)
            
            # Get random reason for the leave type
            reason = random.choice(reasons[leave_type])
            
            # Random status (more pending than others for realistic admin workload)
            status_weights = ['pending'] * 5 + ['approved'] * 3 + ['rejected'] * 2
            status = random.choice(status_weights)
            
            try:
                # Check if leave request already exists for this employee and dates
                existing_leave = LeaveRequest.objects.filter(
                    employee=employee,
                    start_date=start_date,
                    end_date=end_date
                ).first()
                
                if not existing_leave:
                    leave_request = LeaveRequest.objects.create(
                        employee=employee,
                        leave_type=leave_type,
                        start_date=start_date,
                        end_date=end_date,
                        reason=reason,
                        status=status
                    )
                    
                    # If approved or rejected, set approval details
                    if status in ['approved', 'rejected']:
                        # Get a staff user as approver (preferably admin)
                        admin_users = User.objects.filter(is_staff=True)
                        if admin_users.exists():
                            leave_request.approved_by = admin_users.first()
                            if status == 'rejected':
                                leave_request.admin_comments = 'Request does not meet company policy requirements.'
                            else:
                                leave_request.admin_comments = 'Request approved as per company policy.'
                            leave_request.save()
                    
                    leave_requests_created += 1
                    
                    self.stdout.write(
                        f'Created {leave_type} leave for {employee.user.get_full_name()} '
                        f'({start_date} to {end_date}) - Status: {status}'
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create leave request: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {leave_requests_created} sample leave requests!'
            )
        )
        
        # Show summary
        total_leaves = LeaveRequest.objects.count()
        pending_leaves = LeaveRequest.objects.filter(status='pending').count()
        approved_leaves = LeaveRequest.objects.filter(status='approved').count()
        rejected_leaves = LeaveRequest.objects.filter(status='rejected').count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nLeave Request Summary:'
                f'\n  Total: {total_leaves}'
                f'\n  Pending: {pending_leaves}'
                f'\n  Approved: {approved_leaves}'
                f'\n  Rejected: {rejected_leaves}'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ You can now access the admin panel at /admin-dashboard/ to manage leave requests!'
            )
        )
