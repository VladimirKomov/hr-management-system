from django.contrib.auth.models import User
from django.db import models


# Должность - Возможные варианты: Менеджер, Senior-разработчик, Middle-разработчик, Junior-разработчик
class Position(models.TextChoices):
    MANAGER = "Менеджер", "Менеджер"
    SENIOR = "Senior-разработчик", "Senior-разработчик"
    MIDDLE = "Middle-разработчик", "Middle-разработчик"
    JUNIOR = "Junior-разработчик", "Junior-разработчик"


# Специализация - Возможные варианты: Python, DevOps
class Specialization(models.TextChoices):
    PYTHON = "Python", "Python"
    DEVOPS = "DevOps", "DevOps"


# Город - Доступные города: Москва, Санкт-Петербург, Париж
class City(models.TextChoices):
    MOSCOW = "Москва", "Москва"
    SPB = "Санкт-Петербург", "Санкт-Петербург"
    PARIS = "Париж", "Париж"


# Страна - Россия, Франция
class Country(models.TextChoices):
    RUSSIA = "Россия", "Россия"
    FRANCE = "Франция", "Франция"


# Рабочее место - Адрес полностью. Город + Страна: Москва, Россия
class Location(models.Model):
    city = models.CharField("Город", max_length=50, unique=True)
    country = models.CharField("Страна", max_length=50)

    def __str__(self):
        return f"{self.city}, {self.country}"


# Конкретный сотрудник - информацию о конкретном сотруднике
class Employee(models.Model):
    full_name = models.CharField("ФИО полностью", max_length=100)
    position = models.CharField("Должность", max_length=30, choices=Position.choices)
    specialization = models.CharField("Специализация", max_length=30, choices=Specialization.choices)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name="Рабочее место")
    telegram_nick = models.CharField("Ник в Telegram", max_length=50, blank=True, null=True)
    about = models.TextField("О себе", blank=True, null=True)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name="Руководитель"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee"
    )

    def __str__(self):
        return self.full_name
