import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

import scheduled


TZ = ZoneInfo("Europe/Madrid")


class FakeClient:
    def __init__(self, **kwargs):
        self.book_calls = []
        self.kwargs = kwargs

    def get_classes(self, target_day, family_id=None):
        return [
            {
                "timeid": "1715",
                "className": "Weightlifting",
                "bookState": 0,
                "id": "class-123",
            }
        ]

    def book_class(self, target_day, class_id, family_id=None):
        self.book_calls.append((target_day, class_id, family_id))


def config():
    return {
        "timezone": "Europe/Madrid",
        "box_name": "studiocrossfit",
        "box_id": 9507,
        "family_id": None,
        "dry_run": True,
        "window_minutes": 30,
        "bookings": [
            {
                "date": "2026-11-04",
                "opens_at": "2026-11-01T17:15:00",
                "time": "17:15",
                "name": "Weightlifting",
            }
        ],
    }


def test_does_nothing_before_opening_without_credentials(monkeypatch):
    monkeypatch.delenv("EMAIL", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)
    scheduled.run(config(), now=datetime(2026, 11, 1, 17, 14, tzinfo=TZ))


def test_due_booking_uses_dry_run_by_default(monkeypatch, caplog):
    caplog.set_level(logging.INFO, logger="fitbot")
    monkeypatch.setenv("EMAIL", "test@example.com")
    monkeypatch.setenv("PASSWORD", "not-a-real-password")
    monkeypatch.delenv("DRY_RUN", raising=False)
    clients = []

    def factory(**kwargs):
        client = FakeClient(**kwargs)
        clients.append(client)
        return client

    scheduled.run(
        config(),
        now=datetime(2026, 11, 1, 17, 20, tzinfo=TZ),
        client_class=factory,
    )

    assert len(clients) == 1
    assert "DRY RUN: would book 17:15 Weightlifting" in caplog.text
    assert clients[0].book_calls == []


def test_already_booked_class_is_not_booked(monkeypatch):
    monkeypatch.setenv("EMAIL", "test@example.com")
    monkeypatch.setenv("PASSWORD", "not-a-real-password")

    class AlreadyBookedClient(FakeClient):
        def get_classes(self, target_day, family_id=None):
            return [
                {
                    "timeid": "1715",
                    "className": "Weightlifting",
                    "bookState": 1,
                    "id": "class-123",
                }
            ]

    client = AlreadyBookedClient()
    scheduled.run(
        config(),
        now=datetime(2026, 11, 1, 17, 20, tzinfo=TZ),
        client_class=lambda **kwargs: client,
    )
    assert client.book_calls == []


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        scheduled.run(config(), now=datetime(2026, 11, 1, 17, 20))
