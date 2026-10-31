import json
import os
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from client import AimHarderClient
from exceptions import BookingFailed, BoxClosed, NoBookingGoal
from logger import logger
from main import get_class_to_book

CONFIG_PATH = Path(__file__).resolve().parents[1] / "reservas.json"


def load_config(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as config_file:
        return json.load(config_file)


def parse_local_datetime(value, timezone):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone)
    return parsed.astimezone(timezone)


def run(config, now=None, client_class=None):
    timezone = ZoneInfo(config.get("timezone", "Europe/Madrid"))
    now = now or datetime.now(timezone)
    if now.tzinfo is None:
        raise ValueError("The current time must include a timezone")
    now = now.astimezone(timezone)

    window_minutes = int(config.get("window_minutes", 30))
    due_bookings = []
    for booking in config["bookings"]:
        opens_at = parse_local_datetime(booking["opens_at"], timezone)
        elapsed = now - opens_at
        if timedelta(0) <= elapsed <= timedelta(minutes=window_minutes):
            due_bookings.append(booking)

    if not due_bookings:
        logger.info("No bookings are due in the current time window.")
        return

    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    if not email or not password:
        raise RuntimeError(
            "EMAIL and PASSWORD must be configured as GitHub Actions secrets."
        )

    client_class = client_class or AimHarderClient
    client = client_class(
        email=email,
        password=password,
        box_id=int(config["box_id"]),
        box_name=config["box_name"],
        proxy=os.environ.get("PROXY") or None,
    )
    dry_run = (
        os.environ.get("DRY_RUN", str(config.get("dry_run", True))).lower() == "true"
    )

    for booking in due_bookings:
        target_day = datetime.combine(
            date.fromisoformat(booking["date"]), time.min, tzinfo=timezone
        )
        target_time = booking["time"].replace(":", "")
        class_name = booking["name"]

        try:
            classes = client.get_classes(target_day, config.get("family_id"))
            selected_class = get_class_to_book(classes, target_time, class_name)
        except (BoxClosed, NoBookingGoal) as error:
            logger.error(
                "Could not identify %s on %s: %s",
                class_name,
                booking["date"],
                error,
            )
            continue

        if selected_class.get("bookState") == 1:
            logger.info(
                "Already booked: %s %s on %s",
                booking["time"],
                class_name,
                booking["date"],
            )
            continue

        if dry_run:
            logger.info(
                "DRY RUN: would book %s %s on %s (class id %s)",
                booking["time"],
                class_name,
                booking["date"],
                selected_class["id"],
            )
            continue

        try:
            client.book_class(
                target_day,
                selected_class["id"],
                config.get("family_id"),
            )
            logger.info(
                "Booking request sent: %s %s on %s",
                booking["time"],
                class_name,
                booking["date"],
            )
        except BookingFailed as error:
            logger.error(
                "Booking failed for %s on %s: %s",
                class_name,
                booking["date"],
                error,
            )


if __name__ == "__main__":
    run(load_config())
