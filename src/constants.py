LOGIN_ENDPOINT = "https://aimharder.com/login"

ERROR_TAG_ID = "loginErrors"


def book_endpoint(box_name):
    return f"https://{box_name}.aimharder.com/api/book"


def classes_endpoint(box_name):
    return f"https://{box_name}.aimharder.com/api/bookings"


class ErrorMessages:
    TOO_MANY_WRONG_ATTEMPTS = "demasiadas veces"
    INCORRECT_CREDENTIALS = "incorrecto"
