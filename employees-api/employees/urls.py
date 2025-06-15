from django.urls import path
from employees.views import EmployeeListView

urlpatterns = [
    path("", EmployeeListView.as_view(), name="employee-list"),
]
