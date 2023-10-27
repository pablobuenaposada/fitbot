import argparse
import json
import logging
import sys
from datetime import datetime, timedelta

from booking_goals import transform_yaml_to_dict
from client import AimHarderClient
from exceptions import (
    NoBookingGoal,
    NoClassOnTargetDayTime,
    BoxClosed,
    BookingFailed,
    MESSAGE_BOX_IS_CLOSED,
    DayOff,
    InvalidBookingGoals,
)


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
            f"There is no booking-goal for {day.strftime('%A, %Y-%m-%d')}."
        )


def get_class_to_book(classes: list[dict], target_time: str, class_name: str):
    if not classes or len(classes) == 0:
        raise BoxClosed(MESSAGE_BOX_IS_CLOSED)

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


def load_text_file_content(text_file_path):
    if text_file_path is None:
        return []

    try:
        with open(text_file_path, "r") as file:
            # Read the lines of the file, stripping any leading/trailing whitespace
            lines = [line.strip() for line in file.readlines()]
            return lines
    except FileNotFoundError:
        logging.info(f"File not found: {text_file_path}")
        raise FileNotFoundError
        # return []


def validate_target_day(target_day, days_off_file):
    """
    Check target_day is not a day off
    """
    days_off = load_text_file_content(days_off_file)
    if target_day.strftime("%Y-%m-%d") in days_off:
        raise DayOff(
            f"The date {target_day.strftime('%A, %Y-%m-%d')} is among your days off"
            " list so don't book anything"
        )


def main(
    email,
    password,
    box_name,
    box_id,
    days_in_advance,
    booking_goals=None,
    booking_goals_yaml_file=None,
    family_id=None,
    days_off_file=None,
):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if not booking_goals and not booking_goals_yaml_file:
        logging.error(
            "Provide your booking goals using either --booking-goals-yaml-file or"
            " --booking-goals"
        )
        sys.exit(1)

    if booking_goals_yaml_file:
        try:
            with open(booking_goals_yaml_file, "r") as file:
                booking_goals = transform_yaml_to_dict(file)
        except FileNotFoundError:
            logging.info(f"File not found: {booking_goals_yaml_file}")
            raise FileNotFoundError

    target_day = datetime.today() + timedelta(days=days_in_advance)
    try:
        # We get the class time and name we want to book
        target_time, target_name = get_booking_goal_time(target_day, booking_goals)
        validate_target_day(target_day, days_off_file)
        logging.info(
            f"Found date ({target_day.strftime('%A, %Y-%m-%d')}), "
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
    except DayOff as e:
        logging.error(e)
        sys.exit(0)
    except (
        NoClassOnTargetDayTime,
        BoxClosed,
        NoBookingGoal,
        BookingFailed,
        InvalidBookingGoals,
    ) as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    """
    python src/main.py
     --email your.email@mail.com
     --password 1234
     --box-name lahuellacrossfit
     --box-id 3984
     --booking-goal '{"0":{"time": "1815", "name": "Provenza"}}'
     --booking-goal-yaml-file /path/booking-goals.yaml
     --family-id 123456
     --days-off-file /path/days-off.txt'
    """
    parser = argparse.ArgumentParser(
        description="CLI tool to book classes on AimHarder"
    )

    parser.add_argument(
        "--email", required=True, type=str, help="User's email address registered"
    )
    parser.add_argument("--password", required=True, type=str, help="User's password")
    parser.add_argument(
        "--booking-goals",
        required=False,
        type=json.loads,
        help=(
            "JSON representation of booking goals. "
            "You have to provide either --booking-goals-yaml-file or --booking-goals "
            "and --booking-goals-yaml-file has preference."
        ),
    )
    parser.add_argument(
        "--booking-goals-yaml-file",
        required=False,
        type=str,
        help=(
            "Path to a YAML file with the booking goals. "
            "You have to provide either --booking-goals-yaml-file or --booking-goals "
            "and --booking-goals-yaml-file has preference."
        ),
    )
    parser.add_argument("--box-name", required=True, type=str, help="Name of the box")
    parser.add_argument("--box-id", required=True, type=int, help="ID of the box")
    parser.add_argument(
        "--days-in-advance",
        required=True,
        type=int,
        default=3,
        help="Number of days in advance to book",
    )
    parser.add_argument(
        "--family-id",
        required=False,
        type=int,
        default=None,
        help="ID of the family member (optional)",
    )
    parser.add_argument(
        "--days-off-file",
        required=False,
        type=str,
        default=None,
        help=(
            "File containing days off (optional) - Plain text file with a date per line"
            " with the format YYYY-MM-dd. On these days we won't book any classes."
        ),
    )

    args = parser.parse_args()
    input = {key: value for key, value in args.__dict__.items() if value is not None}
    main(**input)
