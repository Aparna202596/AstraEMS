from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN    = 'admin',    'Admin'
    HR       = 'hr',       'HR'
    MANAGER  = 'manager',  'Manager'
    EMPLOYEE = 'employee', 'Employee'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role  = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"