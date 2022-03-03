import datetime
from contextlib import nullcontext as does_not_raise
from http import HTTPStatus
from unittest.mock import patch

import pytest
from requests import Session

from client import AimHarderClient
from exceptions import BookingFailed, IncorrectCredentials, TooManyWrongAttempts

from constants import ErrorMessages

from constants import ERROR_TAG_ID


class TestAimHarderClient:
    @pytest.mark.parametrize(
        "response, expectation",
        (
            (f'<span id="{ERROR_TAG_ID}"></span>', does_not_raise()),
            (
                f'<span id="{ERROR_TAG_ID}">{ErrorMessages.TOO_MANY_WRONG_ATTEMPTS}</span>',
                pytest.raises(TooManyWrongAttempts),
            ),
            (
                f'<span id="{ERROR_TAG_ID}">{ErrorMessages.INCORRECT_CREDENTIALS}</span>',
                pytest.raises(IncorrectCredentials),
            ),
        ),
    )
    def test_init(self, response, expectation):
        with expectation, patch("requests.Session.post") as m_post:
            m_post.return_value.content = response
            # m_post.return_value.status_code = 500
            AimHarderClient(email="foo", password="bar")

    @pytest.mark.parametrize(
        "response, expectation, expected_result",
        (
            ('<span id="loginErrors"></span>', does_not_raise(), Session),
            (
                '<span id="loginErrors">demasiadas veces</span>',
                pytest.raises(TooManyWrongAttempts),
                None,
            ),
            (
                '<span id="loginErrors">incorrecto</span>',
                pytest.raises(IncorrectCredentials),
                None,
            ),
        ),
    )
    def test__login(self, response, expectation, expected_result):
        with expectation, patch("requests.Session.post") as m_post:
            m_post.return_value.content = response
            result = AimHarderClient._login(email="foo", password="bar")
            if not expected_result:
                assert isinstance(result, expected_result)

    @pytest.mark.parametrize(
        "response, expected_classes",
        (
            (
                {},
                None,
            ),
            (
                {"bookings": []},
                [],
            ),
            (
                {"bookings": [{"id": 123, "timeid": "1100_60"}]},
                [{"id": 123, "timeid": "1100_60"}],
            ),
        ),
    )
    def test_get_classes(self, response, expected_classes):
        # mock login
        with patch("requests.Session.post") as m_post:
            m_post.return_value.content = '<span id="loginErrors"></span>'
            client = AimHarderClient(email="foo", password="bar")

        with patch("requests.Session.get") as m_get:
            m_get.return_value.json.return_value = response
            assert client.get_classes(datetime.datetime(2022, 3, 2)) == expected_classes

    @pytest.mark.parametrize(
        "response, status_code, expectation",
        (
            (
                None,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                pytest.raises(BookingFailed),
            ),
            (
                {},
                HTTPStatus.OK,
                pytest.raises(BookingFailed),
            ),
            (
                {"bookState": 0},
                HTTPStatus.OK,
                pytest.raises(BookingFailed),
            ),
            (
                {"errorMssg": "foo"},
                HTTPStatus.OK,
                pytest.raises(BookingFailed),
            ),
            (
                {"errorMssgLang": "foo"},
                HTTPStatus.OK,
                pytest.raises(BookingFailed),
            ),
            (
                {"bookState": 1},
                HTTPStatus.OK,
                does_not_raise(),
            ),
        ),
    )
    def test_book_class(self, response, status_code, expectation):
        # mock login
        with patch("requests.Session.post") as m_post:
            m_post.return_value.content = '<span id="loginErrors"></span>'
            client = AimHarderClient(email="foo", password="bar")

        with patch("requests.Session.post") as m_post:
            m_post.return_value.json.return_value = response
            m_post.return_value.status_code = status_code
            with expectation:
                client.book_class("20220304", "123")
