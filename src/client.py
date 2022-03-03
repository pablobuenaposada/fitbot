from datetime import datetime

from bs4 import BeautifulSoup
from requests import Session

from constants import LOGIN_ENDPOINT, book_endpoint, trainings_endpoint
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
        soup = BeautifulSoup(response.content, "html.parser").find(id="loginErrors")
        if soup is not None:
            match soup.text:
                case "demasiadas veces":
                    raise TooManyWrongAttempts
                case "incorrecto":
                    raise IncorrectCredentials
        return session

    def get_trainings_for_day(self, day: datetime):
        self.target_day = day.strftime("%Y%m%d")
        response = self.session.get(
            trainings_endpoint(BOX["name"]),
            params={
                "box": BOX["id"],
                "day": self.target_day,
                "familyId": "",
            },
        )
        trainings = response.json().get("bookings")
        return trainings

    def book_training(self, target_day: str, training_id: str) -> bool:
        response = self.session.post(
            book_endpoint(BOX["name"]),
            data={
                "id": training_id,
                "day": target_day,
                "insist": 0,
                "familyId": "",
            },
        )
        if response.status_code == 200:
            response = response.json()
            if (
                "bookState" in response
                and response["bookState"] > 0
                and "errorMssg" not in response
                and "errorMssgLang" not in response
            ):
                return
        raise BookingFailed
