import pytest

from booking_goals import transform_yaml_to_dict
from exceptions import InvalidBookingGoals


class TestTransformBookingGoals:
    @pytest.mark.parametrize(
        "input_yaml, expected_dict",
        (
            (
                """
                Monday:
                  "9:00": wod
                friDAY:
                  "15:30": functional
                viernes:
                  "12:12": wod
                """,
                {
                    "0": {"name": "wod", "time": "900"},
                    "4": {"name": "functional", "time": "1530"},
                },
            ),
        ),
    )
    def test_transform_yaml_to_dict(self, input_yaml, expected_dict):
        result = transform_yaml_to_dict(input_yaml)
        assert result == expected_dict

    @pytest.mark.parametrize(
        "input_yaml, expectation",
        (
            (
                "",
                pytest.raises(InvalidBookingGoals),
            ),
            (
                """
                Segunda-feira:
                  "9:00": wod
                viernes:
                  "12:12": wod
                """,
                pytest.raises(InvalidBookingGoals),
            ),
        ),
    )
    def test_transform_yaml_to_dict_invalid_values(self, input_yaml, expectation):
        with expectation:
            transform_yaml_to_dict(input_yaml)
