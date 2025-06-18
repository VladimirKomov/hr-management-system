import logging

from rest_framework import serializers

from employees.models import (
    Employee,
    Position,
    Specialization,
    Location,
    City,
    Country,
)

logger = logging.getLogger("employees")


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


class EmployeeDetailSerializer(serializers.ModelSerializer):
    manager_id = serializers.IntegerField(source='manager.id', read_only=True)
    manager_full_name = serializers.CharField(source='manager.full_name', read_only=True)
    location_full = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "position",
            "specialization",
            "manager_id",
            "manager_full_name",
            "location_full",
            "telegram_nick",
            "about",
        ]

    def get_location_full(self, obj):
        return f"{obj.location.city}, {obj.location.country}"


class EmployeeCreateSerializer(serializers.ModelSerializer):
    city = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            "full_name",
            "position",
            "specialization",
            "city",
            "country",
            "telegram_nick",
            "about",
        ]

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Поле 'ФИО' не может быть пустым.")
        return value

    def validate_telegram_nick(self, value):
        if value:
            value = value.strip()
            if not value.startswith("@") or len(value) <= 1:
                raise serializers.ValidationError("Ник должен начинаться с '@' и содержать хотя бы один символ после.")
        return value

    def validate_position(self, value):
        value_cleaned = value.strip().lower()
        for internal_value, _ in Position.choices:
            if internal_value.lower() == value_cleaned:
                return internal_value
        raise serializers.ValidationError(
            f"Недопустимая должность: {value}. Допустимые значения: {[val for val, _ in Position.choices]}"
        )

    def validate_specialization(self, value):
        value_cleaned = value.strip().lower()
        for internal_value, _ in Specialization.choices:
            if internal_value.lower() == value_cleaned:
                return internal_value
        raise serializers.ValidationError(
            f"Недопустимая специализация: {value}. Допустимые: {[val for val, _ in Specialization.choices]}"
        )

    def validate_city(self, value):
        value_cleaned = value.strip().title()
        allowed = [c for c, _ in City.choices]
        if value_cleaned not in allowed:
            raise serializers.ValidationError(
                f"Недопустимый город: {value}. Допустимые значения: {allowed}"
            )
        return value_cleaned

    def validate_country(self, value):
        value_cleaned = value.strip().title()
        allowed = [c for c, _ in Country.choices]
        if value_cleaned not in allowed:
            raise serializers.ValidationError(
                f"Недопустимая страна: {value}. Допустимые значения: {allowed}"
            )
        return value_cleaned

    def create(self, validated_data):
        city = validated_data.pop("city")
        country = validated_data.pop("country")
        manager = validated_data.pop("manager", None)

        logger.debug(f"[CREATE INPUT] Попытка создания сотрудника: {validated_data}, город: {city}, страна: {country}")

        try:
            location = Location.objects.get(city=city, country=country)
        except Location.DoesNotExist:
            logger.warning(f"[CREATE] Локация не найдена: {city}, {country}")
            raise serializers.ValidationError({
                "location": f"Локация '{city}, {country}' не найдена в системе."
            })

        employee = Employee.objects.create(
            location=location,
            manager=manager,
            **validated_data
            )

        logger.info(f"[CREATE] Сотрудник создан: {employee.full_name} (id={employee.id})")
        return employee
