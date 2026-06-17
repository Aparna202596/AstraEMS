from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    manager_email = serializers.EmailField(source='manager.email', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = [
            'id', 'name', 'description',
            'manager', 'manager_email',
            'employee_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_employee_count(self, obj):
        return obj.employees.count()