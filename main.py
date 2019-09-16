import requests
from datetime import datetime, timedelta

import constants
import settings

# calculate target day
target_day = datetime.today() + timedelta(days=3)
target_day_str = target_day.strftime("%Y%m%d")
target_day_of_the_week = target_day.weekday()

# login
session = requests.Session()
session.post(
    constants.LOGIN_ENDPOINT,
    data={"login": "Log in", "mail": settings.EMAIL, "pw": settings.PASSWORD},
)

# get available classes for target day
classes = session.get(
    constants.CLASSES_ENDPOINT,
    params={"day": target_day_str, "familyId": "", "box": settings.BOX_ID},
)
classes = classes.json()["bookings"]

# try to book a class
for _class in classes:
    for goal in settings.BOOKING_GOALS:
        goal_time = goal.get(target_day_of_the_week, None)
        if (
            goal_time is not None and goal_time in _class["timeid"]
        ):  # if this class is a match for this user book it
            response = session.post(
                constants.BOOK_ENDPOINT,
                data={
                    "id": _class["id"],
                    "day": target_day_str,
                    "insist": 0,
                    "familiId": "",
                },
            )
            if response.status_code == 200 and response.json()["bookState"]:
                print(
                    f'Session booked for {settings.EMAIL} on {target_day_str} at {_class["timeid"]}'
                )
            else:
                print(
                    f"Found a matching session for {settings.EMAIL} on {target_day_str} but something went wrong"
                )
