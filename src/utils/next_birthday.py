from datetime import date


def get_next_birthday(birthday: date, today: date) -> date:
    """Calculate the next occurrence of a birthday relative to today."""
    try:
        next_birthday = birthday.replace(year=today.year)
    except ValueError:
        next_birthday = birthday.replace(year=today.year, day=28)

    if next_birthday < today:
        try:
            next_birthday = birthday.replace(year=today.year + 1)
        except ValueError:
            next_birthday = birthday.replace(year=today.year + 1, day=28)

    return next_birthday
