from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from employees.models import Employee
from employees.serializers import EmployeeListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class EmployeePagination(PageNumberPagination):
    page_size = 5


class EmployeeListView(ListAPIView):
    queryset = Employee.objects.select_related("manager", "location").order_by("full_name")
    serializer_class = EmployeeListSerializer
    pagination_class = EmployeePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "position": ["exact"],
        "specialization": ["exact"],
        "location__city": ["exact"],
        "manager": ["exact"],
    }
