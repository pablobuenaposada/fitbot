import argparse
import json
import logging
from datetime import datetime, timedelta


from client import AimHarderClient
from exceptions import (
    NoBookingGoal,
    BoxClosed,
    MESSAGE_BOX_IS_CLOSED,
    MESSAGE_ALREADY_BOOKED_FOR_TIME,
)
from exceptions import BookingFailed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
    datefmt="%m-%d-%Y %I:%M:%S %p %Z",
)
logger = logging.getLogger(__name__)


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
    return _class[0]


def main(
    email, password, booking_goals, box_name, box_id, days_in_advance, family_id=None
):
    target_day = datetime.today() + timedelta(days=days_in_advance)
    try:
        target_time, target_name = get_booking_goal_time(target_day, booking_goals)
    except NoBookingGoal as e:
        logger.info(str(e))
        return
    client = AimHarderClient(
        email=email, password=password, box_id=box_id, box_name=box_name
    )
    classes = client.get_classes(target_day, family_id)
    _class = get_class_to_book(classes, target_time, target_name)
    if _class["bookState"] == 1:
        logger.info("Class already booked. Nothing to do")
        return
    try:
        client.book_class(target_day, _class["id"], family_id)
    except BookingFailed as e:
        if str(e) == MESSAGE_ALREADY_BOOKED_FOR_TIME:
            logger.error("You are already booked for this time")
            return
        else:
            raise e
    logger.info("Class booked successfully")


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
