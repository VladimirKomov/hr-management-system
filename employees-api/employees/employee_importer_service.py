import csv
import json
import logging
from pathlib import Path

from django.core.exceptions import ValidationError

from employees.models import Employee, Location

logger = logging.getLogger(__name__)


class BaseEmployeeLoader:
    def __init__(self, file_path, created_by=None):
        self.file_path = Path(file_path)
        self.created_by = created_by
        self.errors = []

    def load_data(self):
        raise NotImplementedError

    def save_to_db(self, data):
        created = []

        for item in data:
            try:
                location, _ = Location.objects.get_or_create(
                    city=item["city"],
                    defaults={"country": item["country"]}
                )
                emp = Employee(
                    full_name=item["full_name"],
                    position=item["position"],
                    specialization=item["specialization"],
                    telegram_nick=item.get("telegram_nick"),
                    about=item.get("about"),
                    location=location,
                    manager=self.created_by,
                )
                emp.full_clean()
                emp.save()
                created.append(emp)
            except ValidationError as e:
                msg = f"Ошибка в {item.get('full_name')}: {e}"
                logger.warning(msg)
                self.errors.append(msg)
            except Exception as e:
                msg = f"Ошибка при добавлении {item.get('full_name')}: {e}"
                logger.error(msg)
                self.errors.append(msg)

        return created


# Reading by parts
class JsonEmployeeLoader(BaseEmployeeLoader):
    def load_data(self):
        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("JSON должен быть списком объектов")

                for item in data:
                    yield item
        except json.JSONDecodeError as e:
            logger.error(f"Невозможно прочитать JSON: {e}")
            raise


# Reading by parts
class CsvEmployeeLoader(BaseEmployeeLoader):
    def load_data(self):
        try:
            with open(self.file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        except csv.Error as e:
            logger.error(f"Ошибка при чтении CSV: {e}")
            raise


def get_loader(file_path, created_by=None) -> BaseEmployeeLoader:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return JsonEmployeeLoader(file_path, created_by)
    elif suffix == ".csv":
        return CsvEmployeeLoader(file_path, created_by)
    else:
        raise ValueError("Поддерживаются только файлы .json и .csv")
