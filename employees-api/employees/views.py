import csv
import io
import logging

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.models import Employee
from employees.serializers import EmployeeListSerializer, EmployeeDetailSerializer, EmployeeCreateSerializer

logger = logging.getLogger("employees")


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
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user
        manager = getattr(user, "employee", None) if user.is_authenticated else None
        serializer.save(manager=manager)


class BulkEmployeeUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            logger.warning("[UPLOAD] Файл не загружен")
            return Response({"error": "Файл не был загружен."}, status=400)

        logger.info(f"[UPLOAD] Файл получен: {file.name} ({file.size} байт)")

        try:
            decoded_file = file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded_file))
        except Exception as e:
            logger.error(f"[UPLOAD] Ошибка чтения файла: {e}")
            return Response({"error": f"Ошибка при чтении файла: {e}"}, status=400)

        user = request.user
        manager = getattr(user, "employee", None) if user.is_authenticated else None

        if manager:
            logger.info(f"[UPLOAD] Создание сотрудников под руководителем: {manager.full_name} (id={manager.id})")
        else:
            logger.info("[UPLOAD] Пользователь без руководителя — manager будет None")

        created = []
        errors = []

        try:
            with transaction.atomic():
                for index, row in enumerate(reader, start=2):
                    serializer = EmployeeCreateSerializer(data=row)
                    if serializer.is_valid():
                        employee = serializer.save(manager=manager)
                        created.append(employee.id)
                        logger.info(f"[UPLOAD] Сотрудник создан: {employee.full_name} (id={employee.id})")
                    else:
                        logger.warning(f"[UPLOAD] Ошибка в строке {index}: {serializer.errors}")
                        errors.append({"line": index, "errors": serializer.errors})
                        raise ValueError("Ошибка валидации — прерываем загрузку")
        except Exception:
            logger.error("[UPLOAD] Загрузка прервана. Все изменения отменены.")
            return Response({
                "created_count": 0,
                "errors": errors or ["Загрузка прервана. Все изменения отменены."]
            }, status=400)

        logger.info(f"[UPLOAD] Всего создано: {len(created)} сотрудников")
        return Response({
            "created_count": len(created),
            "errors": []
        }, status=201)
