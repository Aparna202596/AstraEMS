from django.db import models
from django.conf import settings


def generate_department_id(name: str) -> str:
    """
    Generate a department ID in the format: {FIRST_4_LETTERS_CAPS}{2-digit order}.

    The 2-digit suffix is based on the total number of departments already
    created (i.e. insertion order), so the first department gets 01, the
    second gets 02, and so on.

    Example:
        Procurement  → PROC01   (1st department added)
        Sales        → SALE02   (2nd department added)
        Human Resources → HUMA03 (3rd department added)
    """
    prefix = name.strip().upper().replace(" ", "")[:4].ljust(4, "X")

    # Count existing departments to derive next sequential number
    next_number = Department.objects.count() + 1  # 1-based
    suffix = str(next_number).zfill(2)            # zero-padded to 2 digits

    return f"{prefix}{suffix}"


class Department(models.Model):
    # Auto-generated unique identifier, e.g. "PROC01", "SALE02"
    department_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        db_index=True,
    )
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_departments',
        limit_choices_to={'role': 'manager'},
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Generate department_id only on first creation
        if not self.pk and not self.department_id:
            self.department_id = generate_department_id(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department_id} — {self.name}"