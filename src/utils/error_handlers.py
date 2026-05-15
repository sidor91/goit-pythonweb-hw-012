from sqlalchemy.exc import IntegrityError

def handle_integrity_error(e: IntegrityError):
    error = str(e.orig)

    if "contacts_email_key" in error:
        return "Email already exists"

    if "contacts_phone_key" in error:
        return "Phone already exists"

    if "contacts_first_name_key" in error:
        return "Name already exists"

    return "Integrity error"