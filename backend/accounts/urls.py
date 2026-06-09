from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoggedTokenObtainPairView,
    LogoutView, MeView,
    AdminRegisterView, HRRegisterView,
    ManagerRegisterView, EmployeeSignupView,
    ApproveEmployeeView, PendingEmployeesView,
    AuditLogListView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────
    path('login/',   LoggedTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(),          name='token-refresh'),
    path('logout/',  LogoutView.as_view(),                name='logout'),
    path('me/',      MeView.as_view(),                    name='me'),

    # ── Role-specific registration ─────────────────────
    path('register/admin/',    AdminRegisterView.as_view(),    name='register-admin'),
    path('register/hr/',       HRRegisterView.as_view(),       name='register-hr'),
    path('register/manager/',  ManagerRegisterView.as_view(),  name='register-manager'),
    path('signup/employee/',   EmployeeSignupView.as_view(),   name='signup-employee'),

    # ── Employee approval ─────────────────────────────
    path('employees/pending/',  PendingEmployeesView.as_view(), name='pending-employees'),
    path('employees/approve/',  ApproveEmployeeView.as_view(),  name='approve-employee'),

    # ── Audit Logs ────────────────────────────────────
    path('audit-logs/', AuditLogListView.as_view(), name='audit-logs'),
]