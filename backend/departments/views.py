from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer
from accounts.permissions import IsAdminOrHR, IsAdminOrHROrManager
from auditlogs.utils import log_action


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset         = Department.objects.select_related('manager').all()
    serializer_class = DepartmentSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['name', 'description']
    ordering_fields  = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrHR()]          # only Admin/HR can create
        return [IsAuthenticated()]          # anyone logged in can list

    def perform_create(self, serializer):
        dept = serializer.save()
        log_action(self.request, action='create_department', module='departments',
                   description=f"Created department: {dept.name}")


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Department.objects.select_related('manager').all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminOrHR()]

    def perform_update(self, serializer):
        dept = serializer.save()
        log_action(self.request, action='update_department', module='departments',
                   description=f"Updated department: {dept.name}")

    def perform_destroy(self, instance):
        log_action(self.request, action='delete_department', module='departments',
                   description=f"Deleted department: {instance.name}")
        instance.delete()