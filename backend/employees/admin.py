from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['employee_code', 'full_name', 'department', 'employment_status']
    search_fields = ['first_name', 'last_name', 'employee_code']
    list_filter   = ['department', 'employment_status']
