from django.db import models
from django.conf import settings


class EmploymentStatus(models.TextChoices):
    ACTIVE      = 'active',      'Active'
    ON_LEAVE    = 'on_leave',    'On Leave'
    RESIGNED    = 'resigned',    'Resigned'
    TERMINATED  = 'terminated',  'Terminated'


def generate_employee_code(department) -> str:
    if department is None:
        dept_id = "UNKN00"
    else:
        dept_id = department.department_id

    # Global sequential counter (across all departments)
    global_count = Employee.objects.count() + 1          # 1-based
    global_part  = str(global_count).zfill(6)            # e.g. "000001"

    # Per-department sequential counter
    dept_count = Employee.objects.filter(
        department=department
    ).count() + 1                                         # 1-based
    dept_part  = str(dept_count).zfill(3)                # e.g. "001"

    return f"{dept_id}-{global_part}-{dept_part}"


class Employee(models.Model):
    # Link to auth User — one-to-one
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        limit_choices_to={'role': 'employee'},
    )
    # Auto-generated, e.g. "PROC01-000001-001"
    employee_code = models.CharField(
        max_length=25,
        unique=True,
        editable=False,
        db_index=True,
    )
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    phone       = models.CharField(max_length=20, blank=True)
    department  = models.ForeignKey(
        'departments.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='employees',
    )
    designation = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )
    address           = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['employee_code']

    def save(self, *args, **kwargs):
        # Generate employee_code only on first creation
        if not self.pk and not self.employee_code:
            self.employee_code = generate_employee_code(self.department)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.employee_code} — {self.full_name}"