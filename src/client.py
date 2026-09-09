from datetime import datetime
from http import HTTPStatus

from requests import Session

from constants import (
    LOGIN_ENDPOINT,
    book_endpoint,
    classes_endpoint,
)
from exceptions import (
    MESSAGE_BOOKING_FAILED_NO_CREDIT,
    MESSAGE_BOOKING_FAILED_UNKNOWN,
    MESSAGE_TOO_SOON_TO_BOOK,
    BookingFailed,
    IncorrectCredentials,
    TooManyWrongAttempts,
)
from logger import logger


class AimHarderClient:
    def __init__(
        self,
        email: str,
        password: str,
        box_id: int,
        box_name: str,
        proxy: str | None = None,
    ):
        self.session = self._login(email, password, proxy)
        self.box_id = box_id
        self.box_name = box_name

    @staticmethod
    def _login(email: str, password: str, proxy: str | None = None) -> Session:
        session = Session()
        session.proxies = {"https": proxy}
        logger.info(f"Using proxy: {'yes' if proxy else 'no'}")
        response = session.post(
            LOGIN_ENDPOINT,
            data=f'{{"username":"{email}","password":"{password}","iniframe":0}}',
        )
        if response.status_code != HTTPStatus.OK:
            message = response.json().get("error", {}).get("message", "")
            if TooManyWrongAttempts.key_phrase in message:
                raise TooManyWrongAttempts
            elif IncorrectCredentials.key_phrase in message:
                raise IncorrectCredentials
            response.raise_for_status()
        logger.info("Logged successfully")
        return session

    def get_classes(self, target_day: datetime, family_id: str | None = None):
        response = self.session.get(
            classes_endpoint(self.box_name),
            params={
                "box": self.box_id,
                "day": target_day.strftime("%Y%m%d"),
                "familyId": family_id,
            },
        )
        return response.json().get("bookings")

    def book_class(
        self, target_day: datetime, class_id: str, family_id: str | None = None
    ) -> bool:
        response = self.session.post(
            book_endpoint(self.box_name),
            data={
                "id": class_id,
                "day": target_day.strftime("%Y%m%d"),
                "insist": 0,
                "familyId": family_id,
            },
        )
        if response.status_code == HTTPStatus.OK:
            response = response.json()
            if "bookState" in response and response["bookState"] == -2:
                raise BookingFailed(MESSAGE_BOOKING_FAILED_NO_CREDIT)
            if "bookState" in response and response["bookState"] == -12:
                raise BookingFailed(MESSAGE_TOO_SOON_TO_BOOK)
            if "errorMssg" not in response and "errorMssgLang" not in response:
                # booking went fine
                return
        raise BookingFailed(MESSAGE_BOOKING_FAILED_UNKNOWN)
