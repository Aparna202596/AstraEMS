from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeCreateSerializer
from accounts.permissions import IsAdminOrHR, IsAdminOrHROrManager
from auditlogs.utils import log_action


class EmployeeListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['first_name', 'last_name', 'employee_code', 'department__name']
    ordering_fields = ['employee_code', 'first_name', 'joining_date']

    def get_queryset(self):
        return Employee.objects.select_related(
            'user', 'department'
        ).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateSerializer
        return EmployeeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrHR()]
        return [IsAdminOrHROrManager()]

    def perform_create(self, serializer):
        emp = serializer.save()
        log_action(self.request, action='create_employee_profile', module='employees',
                   description=f"Created profile for: {emp.full_name} ({emp.employee_code})")


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.select_related('user', 'department').all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeCreateSerializer
        return EmployeeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdminOrHROrManager()]
        if self.request.method == 'DELETE':
            return [IsAdminOrHR()]
        return [IsAdminOrHROrManager()]

    def perform_update(self, serializer):
        emp = serializer.save()
        log_action(self.request, action='update_employee', module='employees',
                   description=f"Updated employee: {emp.employee_code}")

    def perform_destroy(self, instance):
        log_action(self.request, action='delete_employee', module='employees',
                   description=f"Deleted employee profile: {instance.employee_code}")
        instance.delete()


class MyProfileView(generics.RetrieveUpdateAPIView):
    """Employee can view and update their own profile only."""
    serializer_class   = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.employee_profile
        except Employee.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("No employee profile found for your account.")

    def perform_update(self, serializer):
        emp = serializer.save()
        log_action(self.request, action='self_update_profile', module='employees',
                   description=f"Employee updated own profile: {emp.employee_code}")