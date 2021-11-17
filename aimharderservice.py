from requests import Session, Response
from datetime import datetime

from settings import BOX, ENDPOINTS


class AimHarderService:
    def __init__(self, email: str, password: str) -> None:
        self.session = Session()
        self.email = email
        self.session = self.__class__._login(email, password)

    @staticmethod
    def _login(email: str, password: str, session=Session()):
        session.post(
            ENDPOINTS['LOGIN'],
            data={
                "login": "Log in",
                "mail": email,
                "pw": password,
            },
        )
        return session

    def get_available_trainings_for_day(self, day: datetime):
        self.target_day = day.strftime("%Y%m%d")
        response = self.session.get(
            ENDPOINTS['CLASSES'],
            params={
                "box": BOX['ID'],
                "day": self.target_day,
                "familyId": "",
            },
        )
        trainings = response.json()["bookings"]
        return trainings

    def __log_book_training_response(self, response, time_id):
        data = response.json()
        has_booked_a_training = (
            response.status_code == 200
            and "bookState" in data
            and data['bookState'] > 0
            and not "errorMssg" in data
            and not "errorMssgLang" in data
        )
        if has_booked_a_training:
            print(f"Session booked for {self.email} on {self.target_day} at {time_id}")
        elif "errorMssg" in data:
            print(
                f"Found a matching session for {self.email} on {self.target_day}, but got the following error: {data['errorMssg']}"
            )
        else:
            print(
                f"Found a matching session for {self.email} on {self.target_day}, but something went wrong"
            )
        return has_booked_a_training

    def book_training(self, training_id: str, time_id) -> bool:
        response = self.session.post(
            ENDPOINTS["BOOK"],
            data={
                "day": self.target_day,
                "familiId": "",
                "id": training_id,
                "insist": 0,
            },
        )
        return self.__log_book_training_response(response, time_id)
