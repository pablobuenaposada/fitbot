import argparse
import json
import logging
from datetime import datetime, timedelta


from client import AimHarderClient
from exceptions import NoBookingGoal, NoClassOnTargetDayTime, BoxClosed, BookingFailed


def get_booking_goal_time(day: datetime, booking_goals):
    """Get the booking goal that satisfies the given day of the week"""
    # Take the future day we want to book the class on  (target_day) and check if it exists in the input json parameters
    try:
        return (
            booking_goals[str(day.weekday())]["time"],
            booking_goals[str(day.weekday())]["name"],
        )
    except KeyError:  # There's nothing to book this day
        raise NoClassOnTargetDayTime(
            f"There is no class to book on {day.strftime('%A, %Y-%m-%d')}. "
            f"Either the time or the name could not be found in the input parameters."
        )


def get_class_to_book(classes: list[dict], target_time: str, class_name: str):
    if len(classes) == 0:
        raise BoxClosed("Box is closed")

    classes = list(filter(lambda _class: target_time in _class["timeid"], classes))
    _class = list(
        filter(
            lambda _class: class_name.lower() in _class["className"].lower(), classes
        )
    )
    if len(_class) == 0:
        raise NoBookingGoal(
            f"No class with the text `{class_name}` in its name at time `{target_time}`"
        )
    return _class[0]["id"]


def main(email, password, booking_goals, box_name, box_id, days_in_advance, family_id):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    target_day = datetime.today() + timedelta(days=days_in_advance)
    try:
        # We get the class time and name we want to book
        target_time, target_name = get_booking_goal_time(target_day, booking_goals)
        logging.info(f"Found date ({target_day.strftime('%A, %Y-%m-%d')}), "
                     f"time ({target_time}) and name class ({target_name}) to book."
        )

        client = AimHarderClient(
            email=email, password=password, box_id=box_id, box_name=box_name
        )

        # We fetch the classes that are scheduled for the target day
        classes = client.get_classes(target_day, family_id)
        # From all the classes fetched, we select the one we want to book.
        class_id = get_class_to_book(classes, target_time, target_name)
        client.book_class(target_day, class_id, family_id)
    except (NoClassOnTargetDayTime, BoxClosed, NoBookingGoal, BookingFailed) as e:
        logging.error(e)


if __name__ == "__main__":
    """
    python src/main.py
     --email your.email@mail.com
     --password 1234
     --box-name lahuellacrossfit
     --box-id 3984
     --booking-goal '{"0":{"time": "1815", "name": "Provenza"}}
     --family_-id 123456'
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, type=str)
    parser.add_argument("--password", required=True, type=str)
    parser.add_argument("--booking-goals", required=True, type=json.loads)
    parser.add_argument("--box-name", required=True, type=str)
    parser.add_argument("--box-id", required=True, type=int)
    parser.add_argument("--days-in-advance", required=True, type=int, default=3)
    parser.add_argument("--family-id", required=False, type=int, default=None)
    args = parser.parse_args()
    input = {key: value for key, value in args.__dict__.items() if value != ""}
    main(**input)
