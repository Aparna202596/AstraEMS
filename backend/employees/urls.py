from django.urls import path
from .views import EmployeeListCreateView, EmployeeDetailView, MyProfileView

urlpatterns = [
    path('',           EmployeeListCreateView.as_view(), name='employee-list'),
    path('<int:pk>/',  EmployeeDetailView.as_view(),     name='employee-detail'),
    path('me/',        MyProfileView.as_view(),          name='my-profile'),
]