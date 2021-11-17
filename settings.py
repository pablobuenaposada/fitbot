ACCOUNT = {
    "EMAIL": "your_email@domain.com",
    "PASSWORD": "12345",
}

# La huella aribau
BOX = {
    "ID": 9316,
    "NAME": "lahuellaaribau",
}

BOOKING_GOALS = (
    # mondays at 17:00
    {"day_of_week": 0, "filters": {"timeid": "1700"}},
)

# Do not touch these
ENDPOINTS = {
    "LOGIN": "https://aimharder.com/login",
    "BOOK": f"https://{BOX['ID']}.aimharder.com/api/book",
    "CLASSES": f"https://{BOX['NAME']}.aimharder.com/api/bookings",
}
