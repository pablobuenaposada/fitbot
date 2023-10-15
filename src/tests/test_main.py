import datetime
from contextlib import nullcontext as does_not_raise
from http import HTTPStatus
from unittest.mock import patch, Mock

import pytest
from freezegun import freeze_time

from constants import LOGIN_ENDPOINT
from constants import book_endpoint
from exceptions import NoBookingGoal, BoxClosed, NoClassOnTargetDayTime, DayOff
from main import get_booking_goal_time, validate_target_day
from main import get_class_to_book
from main import load_days_off
from main import main


class TestGetBookingGoalTime:
    @pytest.mark.parametrize(
        "day, booking_goals, expected_time, expectation",
        (
            (
                datetime.datetime(2022, 2, 28),
                {"0": {"time": "1700", "name": "foo"}},
                ("1700", "foo"),
                does_not_raise(),
            ),
            (
                datetime.datetime(2022, 2, 28),
                {},
                None,
                pytest.raises(NoClassOnTargetDayTime),
            ),
        ),
    )
    def test_get_booking_goal_time(
        self, day, booking_goals, expected_time, expectation
    ):
        with expectation:
            assert get_booking_goal_time(day, booking_goals) == expected_time


class TestGetClassToBook:
    @pytest.mark.parametrize(
        "classes, target_time, class_name, expectation",
        (
            (
                [{"id": 123, "timeid": "1700_60", "className": "foo"}],
                "1700",
                "foo",
                does_not_raise(),
            ),
            (
                [
                    {"id": 123, "timeid": "1700_60", "className": "foo"},
                    {"id": 123, "timeid": "1700_60", "className": "foo"},
                ],
                "1700",
                "foo",
                does_not_raise(),
            ),
            (
                [{"id": 123, "timeid": "1100_60", "className": "foo"}],
                "1700",
                "foo",
                pytest.raises(NoBookingGoal),
            ),
            (
                [],
                "1700",
                "foo",
                pytest.raises(BoxClosed),
            ),
        ),
    )
    def test_get_class_to_book(self, classes, target_time, class_name, expectation):
        with expectation:
            assert get_class_to_book(classes, target_time, class_name) == 123


class TestLoadDaysOff:
    # Create a test fixture to set up a temporary test file
    @pytest.fixture
    def temp_days_off_file(self, tmp_path):
        temp_file = tmp_path / "test_days_off.txt"
        with open(temp_file, "w") as f:
            f.write("2023-09-20\n2023-09-21\n2023-09-22\n")
        yield temp_file

    def test_load_days_off_existing_file(self, temp_days_off_file):
        # Test loading dates from an existing file
        dates = load_days_off(temp_days_off_file)
        expected_dates = ["2023-09-20", "2023-09-21", "2023-09-22"]
        assert dates == expected_dates

    def test_load_days_off_nonexistent_file(self):
        # Test loading from a nonexistent file
        non_existent_file = "non_existent_file.txt"
        with pytest.raises(FileNotFoundError):
            load_days_off(non_existent_file)

    def test_load_days_off_empty_file(self, temp_days_off_file):
        # Test loading from an empty file
        empty_file = temp_days_off_file.parent / "empty_days_off.txt"
        with open(empty_file, "w"):
            pass
        dates = load_days_off(empty_file)
        assert dates == []

    def test_load_days_off_whitespace_file(self, temp_days_off_file):
        # Test loading from a file with whitespace
        whitespace_file = temp_days_off_file.parent / "whitespace_days_off.txt"
        with open(whitespace_file, "w") as f:
            f.write("\n \n \n")
        dates = load_days_off(whitespace_file)
        assert dates == ["", "", ""]


class TestValidateTargetDay:
    @pytest.fixture
    def temp_days_off_file_empty(self, tmp_path):
        temp_file = tmp_path / "empty_days_off.txt"
        with open(temp_file, "w"):
            pass
        yield temp_file

    # Create a fixture to set up a temporary days_off_file
    @pytest.fixture
    def temp_days_off_file(self, tmp_path):
        temp_file = tmp_path / "test_days_off.txt"
        with open(temp_file, "w") as f:
            f.write("2023-09-20\n2023-09-21\n2023-09-22\n")
        yield temp_file

    def test_validate_target_day_empty_days_off_file(self, temp_days_off_file_empty):
        # Test when the days_off file is empty
        target_day = datetime.datetime.today() + datetime.timedelta(days=3)
        validate_target_day(target_day, temp_days_off_file_empty)

    def test_validate_target_day_not_in_days_off(self, temp_days_off_file):
        # Test when target_day is not in the days_off file
        target_day = datetime.datetime.today() + datetime.timedelta(
            days=3
        )  # A date 3 days in advance
        validate_target_day(target_day, temp_days_off_file)

    def test_validate_target_day_in_days_off(self, temp_days_off_file):
        # Test when target_day is in the days_off file
        target_day = datetime.datetime(
            2023, 9, 21
        )  # A date that exists in the days_off file
        with pytest.raises(
            DayOff,
            match=(
                "The date Thursday, 2023-09-21 is among your days off list so don't"
                " book anything"
            ),
        ):
            validate_target_day(target_day, temp_days_off_file)

    def test_validate_target_day_nonexistent_days_off_file(self):
        # Test when the days_off file does not exist
        target_day = datetime.datetime.today() + datetime.timedelta(days=3)
        nonexistent_file = "nonexistent_file.txt"
        with pytest.raises(FileNotFoundError):
            validate_target_day(target_day, nonexistent_file)


class TestMain:
    def mock_request_post(*args, **kwargs):
        if args[1] == LOGIN_ENDPOINT:
            return Mock(content="")
        elif args[1] == book_endpoint("foo"):
            return Mock(json=lambda: {}, status_code=HTTPStatus.OK)

    @freeze_time("2022-03-04")
    def test_main(self):
        with patch("requests.Session.post") as m_post, patch(
            "requests.Session.get"
        ) as m_get:
            m_post.side_effect = self.mock_request_post
            m_get.return_value.status_code = HTTPStatus.OK
            m_get.return_value.json.return_value = {
                "bookings": [{"id": 123, "timeid": "1700_60", "className": "Provenza"}]
            }
            main(
                email="foo",
                password="bar",
                booking_goals={"0": {"time": "1700", "name": "Provenza"}},
                box_name="foo",
                box_id=1,
                days_in_advance=3,
            )
