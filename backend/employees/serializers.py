from rest_framework import serializers
from .models import Employee
from accounts.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    email           = serializers.EmailField(source='user.email', read_only=True)
    username        = serializers.CharField(source='user.username', read_only=True)
    account_status  = serializers.CharField(source='user.status', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    full_name       = serializers.ReadOnlyField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'user', 'email', 'username',
            'employee_code', 'first_name', 'last_name', 'full_name',
            'phone', 'department', 'department_name',
            'designation', 'joining_date', 'employment_status',
            'address', 'emergency_contact', 'account_status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'employee_code', 'created_at', 'updated_at']


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Used by HR/Admin to create an employee profile after account is approved."""

    class Meta:
        model  = Employee
        fields = [
            'user', 'first_name', 'last_name',
            'phone', 'department', 'designation',
            'joining_date', 'address', 'emergency_contact',
        ]

    def validate_user(self, value):
        if value.role != 'employee':
            raise serializers.ValidationError("User must have the employee role.")
        if value.status != 'active':
            raise serializers.ValidationError(
                "Employee account must be approved before creating a profile."
            )
        if hasattr(value, 'employee_profile'):
            raise serializers.ValidationError("This user already has an employee profile.")
        return value

    def create(self, validated_data):
        # Auto-generate employee code: EMP-0001, EMP-0002 ...
        last = Employee.objects.order_by('-id').first()
        next_id = (last.id + 1) if last else 1
        validated_data['employee_code'] = f"EMP-{next_id:04d}"
        return super().create(validated_data)