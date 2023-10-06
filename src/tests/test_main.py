import datetime
from http import HTTPStatus
from unittest.mock import patch, Mock

import pytest

from contextlib import nullcontext as does_not_raise

from exceptions import NoBookingGoal, BoxClosed

from main import get_class_to_book

from main import get_booking_goal_time

from main import main

from freezegun import freeze_time

from constants import LOGIN_ENDPOINT

from constants import book_endpoint


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
                pytest.raises(NoBookingGoal),
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
