import settings

# checking BOX setting
assert type(settings.BOX) == dict
assert "ID" in settings.BOX
assert type(settings.BOX["ID"]) == int
assert "NAME" in settings.BOX
assert type(settings.BOX["NAME"]) == str

# checking ENDPOINTS setting
assert type(settings.ENDPOINTS) == dict
assert "LOGIN" in settings.ENDPOINTS
assert type(settings.ENDPOINTS['LOGIN']) == str
assert "BOOK" in settings.ENDPOINTS
assert type(settings.ENDPOINTS['BOOK']) == str
assert "CLASSES" in settings.ENDPOINTS
assert type(settings.ENDPOINTS['CLASSES']) == str

# checking BOOKING_GOALS setting
assert type(settings.BOOKING_GOALS) == tuple
for booking_goal in settings.BOOKING_GOALS:
    assert type(booking_goal) == dict
    assert "day_of_week" in booking_goal
    assert type(booking_goal["day_of_week"]) == int
    assert "filters" in booking_goal
    assert type(booking_goal["filters"]) == dict
    assert "timeid" in booking_goal["filters"]
    assert type(booking_goal["filters"]["timeid"]) == str

# checking ACCOUNT settings
assert type(settings.ACCOUNT) == dict
assert "EMAIL" in settings.ACCOUNT
assert type(settings.ACCOUNT["EMAIL"]) == str
assert "PASSWORD" in settings.ACCOUNT
assert type(settings.ACCOUNT["PASSWORD"]) == str
