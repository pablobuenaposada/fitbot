from datetime import datetime, timedelta


from settings import ACCOUNT, DAYS_IN_ADVANCE
from client import AimHarderClient
from exceptions import NoBookingGoal
import settings


def get_booking_goal_time(day: datetime, booking_goals):
    """Get the booking goal that satisfies the given day of the week"""
    try:
        return (
            booking_goals[day.weekday()]["time"],
            booking_goals[day.weekday()]["name"],
        )
    except KeyError:  # did not found a matching booking goal
        raise NoBookingGoal


def get_class_to_book(classes: list[dict], target_time: str, class_name: str):
    classes = list(filter(lambda _class: target_time in _class["timeid"], classes))
    _class = list(filter(lambda _class: class_name in _class["className"], classes))
    if len(_class) == 0:
        raise NoBookingGoal
    return _class[0]["id"]


def main():
    target_day = datetime.today() + timedelta(days=DAYS_IN_ADVANCE)
    client = AimHarderClient(email=ACCOUNT["email"], password=ACCOUNT["password"])
    target_time, target_name = get_booking_goal_time(target_day, settings.BOOKING_GOALS)
    classes = client.get_classes(target_day)
    class_id = get_class_to_book(classes, target_time, target_name)
    client.book_class(target_day, class_id)


if __name__ == "__main__":
    main()
