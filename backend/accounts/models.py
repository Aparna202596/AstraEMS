import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Role(models.TextChoices):
    ADMIN    = 'admin',    'Admin'
    HR       = 'hr',       'HR'
    MANAGER  = 'manager',  'Manager'
    EMPLOYEE = 'employee', 'Employee'


class AccountStatus(models.TextChoices):
    ACTIVE   = 'active',   'Active'
    PENDING  = 'pending',  'Pending'   
    INACTIVE = 'inactive', 'Inactive'
    REJECTED = 'rejected', 'Rejected'


def validate_role_email(email, role):
    """Enforce email format rules per role."""
    patterns = {
        Role.ADMIN:   r'^[a-z0-9]+\.admin@astraems\.com$',
        Role.HR:      r'^[a-z0-9]+\.hr@astraems\.com$',
        Role.MANAGER: r'^[a-z0-9]+\.manager@astraems\.com$',
    }
    pattern = patterns.get(role)
    if pattern and not re.match(pattern, email):
        examples = {
            Role.ADMIN:   'john.admin@astraems.com',
            Role.HR:      'jane.hr@astraems.com',
            Role.MANAGER: 'mike.manager@astraems.com',
        }
        raise ValidationError(
            f"{role} email must match format: {examples[role]}"
        )


class User(AbstractUser):
    email  = models.EmailField(unique=True)
    role   = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    status = models.CharField(max_length=20, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)

    # Employee accounts start as PENDING, approved by a manager
    approved_by = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_users',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def clean(self):
        super().clean()
        validate_role_email(self.email, self.role)

    def save(self, *args, **kwargs):
        # New employees start as PENDING
        if self._state.adding and self.role == Role.EMPLOYEE:
            self.status = AccountStatus.PENDING
            self.is_active = False
        # Admin/HR/Manager accounts start active
        elif self._state.adding and self.role in [Role.ADMIN, Role.HR, Role.MANAGER]:
            self.status = AccountStatus.ACTIVE
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"