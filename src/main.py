import argparse
import json
from datetime import datetime, timedelta


from client import AimHarderClient
from exceptions import (
    NoBookingGoal,
    BoxClosed,
    MESSAGE_BOX_IS_CLOSED,
)


def get_booking_goal_time(day: datetime, booking_goals):
    """Get the booking goal that satisfies the given day of the week"""
    try:
        return (
            booking_goals[str(day.weekday())]["time"],
            booking_goals[str(day.weekday())]["name"],
        )
    except KeyError:  # did not find a matching booking goal
        raise NoBookingGoal(
            f"There is no booking-goal for {day.strftime('%A, %Y-%m-%d')}."
        )


def get_class_to_book(classes: list[dict], target_time: str, class_name: str):
    if not classes or len(classes) == 0:
        raise BoxClosed(MESSAGE_BOX_IS_CLOSED)

    classes = list(filter(lambda _class: target_time in _class["timeid"], classes))
    _class = list(filter(lambda _class: class_name in _class["className"], classes))
    if len(_class) == 0:
        raise NoBookingGoal(
            f"No class with the text `{class_name}` in its name at time `{target_time}`"
        )
    return _class[0]["id"]


def main(
    email, password, booking_goals, box_name, box_id, days_in_advance, family_id=None
):
    target_day = datetime.today() + timedelta(days=days_in_advance)
    target_time, target_name = get_booking_goal_time(target_day, booking_goals)
    client = AimHarderClient(
        email=email, password=password, box_id=box_id, box_name=box_name
    )
    classes = client.get_classes(target_day, family_id)
    class_id = get_class_to_book(classes, target_time, target_name)
    client.book_class(target_day, class_id, family_id)


if __name__ == "__main__":
    """
    python src/main.py
     --email your.email@mail.com
     --password 1234
     --box-name lahuellacrossfit
     --box-id 3984
     --booking-goal '{"0":{"time": "1815", "name": "Provenza"}}'
     --family-id 123456
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, type=str)
    parser.add_argument("--password", required=True, type=str)
    parser.add_argument("--booking-goals", required=True, type=json.loads)
    parser.add_argument("--box-name", required=True, type=str)
    parser.add_argument("--box-id", required=True, type=int)
    parser.add_argument("--days-in-advance", required=True, type=int, default=3)
    parser.add_argument(
        "--family-id",
        required=False,
        type=int,
        default=None,
        help="ID of the family member (optional)",
    )
    args = parser.parse_args()
    input = {key: value for key, value in args.__dict__.items() if value != ""}
    main(**input)
