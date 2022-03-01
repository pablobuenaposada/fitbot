LOGIN_ENDPOINT = "https://aimharder.com/login"


def book_endpoint(box_name):
    return f"https://{box_name}.aimharder.com/api/book"


def trainings_endpoint(box_name):
    return f"https://{box_name}.aimharder.com/api/bookings"
