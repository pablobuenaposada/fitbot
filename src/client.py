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
from exceptions import BookingFailed, IncorrectCredentials, TooManyWrongAttempts


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

    def get_classes(self, target_day: datetime):
        response = self.session.get(
            classes_endpoint(self.box_name),
            params={
                "box": self.box_id,
                "day": target_day.strftime("%Y%m%d"),
                "familyId": "",
            },
        )
        return response.json().get("bookings")

    def book_class(self, target_day: datetime, class_id: str) -> bool:
        response = self.session.post(
            book_endpoint(self.box_name),
            data={
                "id": class_id,
                "day": target_day.strftime("%Y%m%d"),
                "insist": 0,
                "familyId": "",
            },
        )
        if response.status_code == HTTPStatus.OK:
            response = response.json()
            if "errorMssg" not in response and "errorMssgLang" not in response:
                return
        raise BookingFailed
