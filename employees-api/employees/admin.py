from django.contrib import admin

from employees.models import Location, Employee


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "country")
    search_fields = ("city", "country")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'specialization', 'location', 'manager')
    search_fields = ('full_name', 'telegram_nick')
    list_filter = ('position', 'specialization', 'location')
