from django.core.management.base import BaseCommand
from faker import Faker
import random

from employees.models import Employee, Location, Position, Specialization

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = "Генерирует и сохраняет случайных сотрудников в базу"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Количество сотрудников')

    def handle(self, *args, **options):
        count = options['count']

        # Step 1 - create locations
        cities = {
            "Москва": "Россия",
            "Санкт-Петербург": "Россия",
            "Париж": "Франция",
        }

        city_objs = {
            name: Location.objects.get_or_create(city=name, defaults={"country": country})[0]
            for name, country in cities.items()
        }

        # Step 2 - create employees
        employees = []

        for _ in range(count):
            full_name = fake.name()
            position = random.choice([pos for pos, _ in Position.choices])
            specialization = random.choice([spec for spec, _ in Specialization.choices])
            city = random.choice(list(city_objs.values()))
            telegram_nick = f"@{fake.unique.user_name()}"
            about = fake.sentence(nb_words=10)

            emp = Employee(
                full_name=full_name,
                position=position,
                specialization=specialization,
                location=city,
                telegram_nick=telegram_nick,
                about=about,
                manager=None,
            )
            employees.append(emp)

        Employee.objects.bulk_create(employees)

        # Step 3 - add managers
        all_employees = list(Employee.objects.order_by("id"))

        for idx, emp in enumerate(all_employees):
            if idx >= 5:
                manager_index = (idx // 5) - 1
                emp.manager = all_employees[manager_index]
                emp.save()

        self.stdout.write(self.style.SUCCESS(f"Создано {len(all_employees)} сотрудников"))
