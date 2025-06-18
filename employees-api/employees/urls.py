from django.urls import path

from employees.views import (
    EmployeeListView,
    EmployeeDetailView,
    EmployeeCreateView,
    BulkEmployeeUploadView,
)

urlpatterns = [
    path("", EmployeeListView.as_view(), name="employee-list"),
    path("<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
    path("create/", EmployeeCreateView.as_view()),
    path("upload/", BulkEmployeeUploadView.as_view(), name="employee-bulk-upload"),
]
