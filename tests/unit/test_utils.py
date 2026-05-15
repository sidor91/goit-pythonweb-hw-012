from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from src.utils.error_handlers import handle_integrity_error
from src.utils.next_birthday import get_next_birthday


def test_handle_integrity_error_variants():
    assert (
        handle_integrity_error(IntegrityError("", {}, Exception("contacts_email_key")))
        == "Email already exists"
    )
    assert (
        handle_integrity_error(IntegrityError("", {}, Exception("contacts_phone_key")))
        == "Phone already exists"
    )
    assert (
        handle_integrity_error(
            IntegrityError("", {}, Exception("contacts_first_name_key"))
        )
        == "Name already exists"
    )
    assert (
        handle_integrity_error(IntegrityError("", {}, Exception("some other error")))
        == "Integrity error"
    )


def test_get_next_birthday_in_current_year():
    today = date.today()
    birthday = today.replace(year=today.year - 20)
    next_date = get_next_birthday(birthday, today)
    assert next_date == birthday.replace(year=today.year)


def test_get_next_birthday_next_year_if_passed():
    today = date(2025, 12, 31)
    birthday = date(1990, 1, 1)
    next_date = get_next_birthday(birthday, today)
    assert next_date == date(2026, 1, 1)
