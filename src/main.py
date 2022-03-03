from datetime import datetime, timedelta
from time import sleep

from aimharderservice import AimHarderService

from settings import ACCOUNT, BOOKING_GOALS


def get_booking_goal(day_of_week: datetime):
    """Get the booking goal that satisfies the given day of the week"""

    booking_goals = [
        goal for goal in BOOKING_GOALS if goal["day_of_week"] == day_of_week.weekday()
    ]
    try:
        return booking_goals[0]
    except IndexError:  # did not found a matching booking goal
        return None


def get_time_to_book_training(booking_goal) -> datetime:
    """
    Returns the date and time when we should book a training
    booking_goal has the following shape
        {"day_of_week": 0, "filters": {"timeid": "1800_60", ...}},
    """

    target_time = booking_goal["filters"]["timeid"].split("_")[0]
    target_time = datetime.strptime(target_time, "%H%M")
    time_to_book = datetime.today().replace(
        hour=target_time.hour, minute=target_time.minute, second=0
    )
    # try to start booking 1 second before the actual training time
    return time_to_book - timedelta(seconds=1)


# This constant depends on the box, you are not allowed to book trainings
# with more than 3 days in advance
DAYS_IN_ADVANCE = 3


def main():
    target_day: datetime = datetime.today() + timedelta(days=DAYS_IN_ADVANCE)

    booking_goal = get_booking_goal(target_day)
    if not booking_goal:
        return
    goal_filters = booking_goal.get("filters", {})

    service = AimHarderService(email=ACCOUNT["EMAIL"], password=ACCOUNT["PASSWORD"])
    trainings = service.get_available_trainings_for_day(target_day)
    time_to_book_training = get_time_to_book_training(booking_goal)

    while datetime.now() < time_to_book_training:
        sleep(0.2)

    training_is_booked = False
    while not training_is_booked:

        for training in trainings:
            should_book_training = all(
                training[filter_name] == filter_value
                for filter_name, filter_value in goal_filters.items()
            )
            if not should_book_training:
                continue

            # training for the class and time we want
            training_is_booked = service.book_training(
                training_id=training["id"],
                time_id=training["timeid"],
            )
        sleep(0.1)


if __name__ == "__main__":
    main()
