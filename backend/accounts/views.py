from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .serializers import (
    AdminRegisterSerializer, HRRegisterSerializer,
    ManagerRegisterSerializer, EmployeeSignupSerializer,
    ApproveEmployeeSerializer, UserSerializer,
)
from .permissions import IsAdmin, IsAdminOrHR, IsAdminOrHROrManager
from auditlogs.utils import log_action

User = get_user_model()


class LoggedTokenObtainPairView(TokenObtainPairView):
    """JWT login — records login event to audit log for all roles."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Fetch the user who just logged in
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email)
                log_action(
                    user, action='login', module='auth',
                    description=f"{user.role} login",
                    extra_data={'ip': _get_ip(request)},
                )
            except User.DoesNotExist:
                pass
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            log_action(request, action='logout', module='auth',
                       description=f"{request.user.role} logout")
            return Response({'detail': 'Logged out successfully.'})
        except Exception:
            return Response({'detail': 'Invalid token.'},
                            status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Registration endpoints (each role has its own) ──────────────────────────

class AdminRegisterView(generics.CreateAPIView):
    """Only existing admins can create another admin."""
    serializer_class   = AdminRegisterSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request, action='create_admin', module='auth',
                   description=f"Created admin account: {user.email}")


class HRRegisterView(generics.CreateAPIView):
    """Only admins can create HR accounts."""
    serializer_class   = HRRegisterSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request, action='create_hr', module='auth',
                   description=f"Created HR account: {user.email}")


class ManagerRegisterView(generics.CreateAPIView):
    """Admins and HR can create manager accounts."""
    serializer_class   = ManagerRegisterSerializer
    permission_classes = [IsAdminOrHR]

    def perform_create(self, serializer):
        user = serializer.save()
        log_action(self.request, action='create_manager', module='auth',
                   description=f"Created manager account: {user.email}")


class EmployeeSignupView(generics.CreateAPIView):
    """Public signup — anyone can register as employee (pending approval)."""
    serializer_class   = EmployeeSignupSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Log signup as anonymous action with new user's info
        log_action(
            user, action='employee_signup', module='auth',
            description=f"New employee signup pending approval: {user.email}",
        )


class ApproveEmployeeView(APIView):
    """Managers (and HR/Admin) approve or reject pending employee signups."""
    permission_classes = [IsAdminOrHROrManager]

    def post(self, request):
        serializer = ApproveEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data['user_id']
        action  = serializer.validated_data['action']

        try:
            employee = User.objects.get(id=user_id, role='employee')
        except User.DoesNotExist:
            return Response({'detail': 'Employee not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            employee.status      = 'active'
            employee.is_active   = True
            employee.approved_by = request.user
            employee.approved_at = timezone.now()
            employee.save()
            log_action(
                request, action='approve_employee', module='auth',
                description=f"Approved employee: {employee.email}",
                extra_data={'employee_id': employee.id},
            )
            return Response({'detail': f'Employee {employee.email} approved.'})

        elif action == 'reject':
            employee.status    = 'rejected'
            employee.is_active = False
            employee.save()
            log_action(
                request, action='reject_employee', module='auth',
                description=f"Rejected employee: {employee.email}",
                extra_data={'employee_id': employee.id},
            )
            return Response({'detail': f'Employee {employee.email} rejected.'})


class PendingEmployeesView(generics.ListAPIView):
    """List all employees awaiting approval."""
    serializer_class   = UserSerializer
    permission_classes = [IsAdminOrHROrManager]

    def get_queryset(self):
        return User.objects.filter(role='employee', status='pending')


# ── Audit Log endpoints ──────────────────────────────────────────────────────

from auditlogs.models import AuditLog
from rest_framework.pagination import PageNumberPagination


class AuditLogPagination(PageNumberPagination):
    page_size = 50


class AuditLogListView(APIView):
    """
    Admin sees ALL logs.
    HR sees logs for all roles.
    Manager sees only their team's logs.
    """
    permission_classes = [IsAdminOrHROrManager]

    def get(self, request):
        role = request.user.role

        if role in ['admin', 'hr']:
            logs = AuditLog.objects.all().order_by('-timestamp')[:200]
        else:
            # Manager sees only employees they approved
            approved_emails = list(
                User.objects.filter(approved_by=request.user)
                            .values_list('email', flat=True)
            )
            approved_emails.append(request.user.email)
            logs = AuditLog.objects.filter(
                user_email__in=approved_emails
            ).order_by('-timestamp')[:100]

        data = [
            {
                'user_email':  log.user_email,
                'user_role':   log.user_role,
                'action':      log.action,
                'module':      log.module,
                'description': log.description,
                'ip_address':  log.ip_address,
                'timestamp':   log.timestamp.isoformat(),
            }
            for log in logs
        ]
        return Response(data)


def _get_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')