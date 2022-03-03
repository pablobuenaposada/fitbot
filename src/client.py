from datetime import datetime
from http import HTTPStatus

from bs4 import BeautifulSoup
from requests import Session

from constants import (
    LOGIN_ENDPOINT,
    book_endpoint,
    classes_endpoint,
    ErrorMessages,
    ERROR_TAG_ID,
)
from exceptions import BookingFailed, IncorrectCredentials, TooManyWrongAttempts
from settings import BOX


class AimHarderClient:
    def __init__(self, email: str, password: str):
        self.session = self._login(email, password)

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
            match soup.text:
                case ErrorMessages.TOO_MANY_WRONG_ATTEMPTS:
                    raise TooManyWrongAttempts
                case ErrorMessages.INCORRECT_CREDENTIALS:
                    raise IncorrectCredentials
        return session

    def get_classes(self, target_day: datetime):
        response = self.session.get(
            classes_endpoint(BOX["name"]),
            params={
                "box": BOX["id"],
                "day": target_day.strftime("%Y%m%d"),
                "familyId": "",
            },
        )
        return response.json().get("bookings")

    def book_class(self, target_day: str, class_id: str) -> bool:
        response = self.session.post(
            book_endpoint(BOX["name"]),
            data={
                "id": class_id,
                "day": target_day,
                "insist": 0,
                "familyId": "",
            },
        )
        if response.status_code == HTTPStatus.OK:
            response = response.json()
            if (
                "bookState" in response
                and response["bookState"] > 0
                and "errorMssg" not in response
                and "errorMssgLang" not in response
            ):
                return
        raise BookingFailed
