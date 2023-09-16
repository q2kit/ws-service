import re


def validate_email(email: str) -> bool:
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return True, None
    else:
        return False, 'Invalid email'


def validate_password(password: str) -> bool:
    if len(password) >= 6:
        return True, None
    else:
        return False, 'Password must be at least 6 characters'
