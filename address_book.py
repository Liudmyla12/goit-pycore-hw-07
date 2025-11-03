from collections import UserDict
from datetime import datetime, timedelta, date


class Field:
    """Базове поле запису (має значення та текстове представлення)."""

    def __init__(self, value: str):
        self._value: str | None = None
        self.value = value  # піде через сеттер (можна розширювати у спадкоємців)

    @property
    def value(self) -> str:
        return self._value  # type: ignore[return-value]

    @value.setter
    def value(self, v: str) -> None:
        self._value = v

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class Name(Field):
    """Ім'я контакту (обов'язкове поле)."""
    def __init__(self, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    """Телефон з валідацією рівно на 10 цифр (умова завдання)."""

    @staticmethod
    def _normalize(s: str) -> str:
        # залишаємо тільки цифри
        return "".join(ch for ch in s if ch.isdigit())

    @Field.value.setter  # перевизначаємо сеттер з валідацією
    def value(self, v: str) -> None:
        digits = self._normalize(v)
        if len(digits) != 10:
            raise ValueError("Phone must contain exactly 10 digits")
        self._value = digits

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Phone):
            return self.value == other.value
        if isinstance(other, str):
            try:
                return self.value == Phone(other).value
            except ValueError:
                return False
        return False


class Birthday(Field):
    """Дата народження у форматі DD.MM.YYYY (необов'язкове поле)."""
    @Field.value.setter
    def value(self, v: str) -> None:
        try:
            dt = datetime.strptime(v, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        self._value = dt  # type: ignore[assignment]

    def __str__(self) -> str:
        # для красивого виводу
        return self.value.strftime("%d.%m.%Y")  # type: ignore[union-attr]


class Record:
    """Запис контакту: ім'я + список телефонів (об'єкти Phone) + (опц.) день народження."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None  # ← додано для HW-07

    # --- методи за вимогами ---
    def add_phone(self, phone: str) -> Phone:
        p = Phone(phone)
        self.phones.append(p)
        return p

    def find_phone(self, phone: str) -> Phone | None:
        try:
            probe = Phone(phone)  # нормалізує та перевіряє
        except ValueError:
            return None
        for p in self.phones:
            if p == probe:
                return p
        return None

    def remove_phone(self, phone: str) -> bool:
        target = self.find_phone(phone)
        if target:
            self.phones.remove(target)
            return True
        return False

    def edit_phone(self, old: str, new: str) -> bool:
        target = self.find_phone(old)
        if not target:
            return False
        # якщо new некоректний — згенерується ValueError (це нормально для перевірки)
        target.value = Phone(new).value
        return True

    # --- нове для HW-07 ---
    def add_birthday(self, date_str: str) -> None:
        self.birthday = Birthday(date_str)

    def __str__(self) -> str:
        phones_part = "; ".join(p.value for p in self.phones) if self.phones else "—"
        bday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_part}{bday}"


class AddressBook(UserDict):
    """Колекція записів (name -> Record)."""

    # додати запис
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    # знайти запис за ім'ям
    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    # видалити запис за ім'ям
    def delete(self, name: str) -> bool:
        if name in self.data:
            del self.data[name]
            return True
        return False

    # --- нове для HW-07 ---
    def get_upcoming_birthdays(self) -> list[tuple[str, str]]:
        """Список (name, DD.MM.YYYY) з днями народження у найближчі 7 днів."""
        today: date = datetime.today().date()
        result: list[tuple[str, str]] = []
        for rec in self.data.values():
            if not rec.birthday:
                continue
            # день народження у поточному році
            bday_this_year = rec.birthday.value.replace(year=today.year)  # type: ignore[union-attr]
            # якщо вже минув — дивимось наступний рік
            if bday_this_year < today:
                bday_this_year = bday_this_year.replace(year=today.year + 1)
            days = (bday_this_year - today).days
            if 0 <= days <= 7:
                result.append((rec.name.value, bday_this_year.strftime("%d.%m.%Y")))
        return result

