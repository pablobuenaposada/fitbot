from datetime import datetime
from http import HTTPStatus

from bs4 import BeautifulSoup
from requests import Session

from constants import (
    LOGIN_ENDPOINT,
    book_endpoint,
    classes_endpoint,
    ERROR_TAG_ID,
)
from exceptions import (
    BookingFailed,
    IncorrectCredentials,
    TooManyWrongAttempts,
    MESSAGE_BOOKING_FAILED_UNKNOWN,
    MESSAGE_BOOKING_FAILED_NO_CREDIT,
)


class AimHarderClient:
    def __init__(self, email: str, password: str, box_id: int, box_name: str):
        self.session = self._login(email, password)
        self.box_id = box_id
        self.box_name = box_name

    @staticmethod
    def _login(email: str, password: str):
        session = Session()
        response = session.post(
            LOGIN_ENDPOINT,
            data={
                "login": "Log in",
                "mail": email,
                "pw": password,
            },
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser").find(id=ERROR_TAG_ID)
        if soup is not None:
            if TooManyWrongAttempts.key_phrase in soup.text:
                raise TooManyWrongAttempts
            elif IncorrectCredentials.key_phrase in soup.text:
                raise IncorrectCredentials
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
            if "errorMssg" not in response and "errorMssgLang" not in response:
                # booking went fine
                return
        raise BookingFailed(MESSAGE_BOOKING_FAILED_UNKNOWN)
