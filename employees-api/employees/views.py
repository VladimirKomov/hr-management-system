from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from employees.models import Employee
from employees.serializers import EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer


class EmployeePagination(PageNumberPagination):
    page_size = 5


class EmployeeListView(ListAPIView):
    permission_classes = [AllowAny]

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


class EmployeeDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]

    queryset = Employee.objects.select_related("manager", "location")
    serializer_class = EmployeeDetailSerializer


class EmployeeCreateView(CreateAPIView):
    serializer_class = EmployeeCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        manager = self.request.user.employee
        serializer.save(manager=manager)
