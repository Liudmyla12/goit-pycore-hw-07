from functools import wraps
from address_book import AddressBook, Record


def input_error(func):
    """Декоратор для дружніх повідомлень про помилки вводу."""
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Value error: {e}"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Missing arguments."
        except Exception as e:
            return f"Error: {e}"
    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    msg = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        msg = "Contact added."
    record.add_phone(phone)
    return msg


@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.edit_phone(old_phone, new_phone):
        return "Phone number updated."
    return "Phone number not found."


@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    phones = "; ".join(p.value for p in record.phones) if record.phones else "—"
    return f"{name}: {phones}"


@input_error
def show_all(_, book: AddressBook):
    if not book.data:
        return "Address book is empty."
    return "\n".join(str(r) for r in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, date_str = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(date_str)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None or record.birthday is None:
        return "No birthday found."
    return f"{name}'s birthday is {record.birthday}"


@input_error
def birthdays(_, book: AddressBook):
    items = book.get_upcoming_birthdays()
    if not items:
        return "No birthdays this week."
    lines = ["Upcoming birthdays:"]
    lines += [f"{name} — {date}" for name, date in items]
    return "\n".join(lines)
