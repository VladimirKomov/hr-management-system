from rest_framework import serializers
from employees.models import Employee

class EmployeeListSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
    city = serializers.CharField(source="location.city")

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "position",
            "specialization",
            "city",
            "manager_name",
        ]

    def get_manager_name(self, obj):
        if obj.manager:
            parts = obj.manager.full_name.split()
            return f"{parts[0]} {''.join(p[0] + '.' for p in parts[1:])}"
        return None
