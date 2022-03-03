import datetime

import pytest

from contextlib import nullcontext as does_not_raise

from exceptions import NoBookingGoal

from main import get_class_to_book

from main import get_booking_goal_time


class TestGetBookingGoalTime:
    @pytest.mark.parametrize(
        "day, booking_goals, expected_time, expectation",
        (
            (
                datetime.datetime(2022, 2, 28),
                {0: {"time": "1700", "name": "foo"}},
                ("1700", "foo"),
                does_not_raise(),
            ),
            (datetime.datetime(2022, 2, 28), {}, None, pytest.raises(NoBookingGoal)),
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
        ),
    )
    def test_get_class_to_book(self, classes, target_time, class_name, expectation):
        with expectation:
            assert get_class_to_book(classes, target_time, class_name) == 123
