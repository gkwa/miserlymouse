import datetime

import pytest

import miserlymouse.clock


@pytest.mark.parametrize(
    "text,expected",
    [
        ("3pm", (15, 0)),
        ("3PM", (15, 0)),
        ("3 p.m.", (15, 0)),
        ("3am", (3, 0)),
        ("12pm", (12, 0)),
        ("12am", (0, 0)),
        ("12.15pm", (12, 15)),
        ("12:15pm", (12, 15)),
        ("1215pm", (12, 15)),
        ("315pm", (15, 15)),
        ("15:00", (15, 0)),
        ("1500", (15, 0)),
        ("00:30", (0, 30)),
        ("noon", (12, 0)),
        ("midnight", (0, 0)),
    ],
)
def test_parses(text: str, expected: tuple[int, int]) -> None:
    assert miserlymouse.clock.parse_time(text) == expected


@pytest.mark.parametrize(
    "text",
    ["", "3", "15", "25:00", "3:75pm", "13pm", "0pm", "teatime", "3pmm", "-3pm"],
)
def test_rejects(text: str) -> None:
    with pytest.raises(miserlymouse.clock.TimeError):
        miserlymouse.clock.parse_time(text)


def local(year: int, month: int, day: int, hour: int, minute: int) -> datetime.datetime:
    naive = datetime.datetime(year, month, day, hour, minute)
    return naive.astimezone()


def test_later_today() -> None:
    now = local(2026, 8, 27, 9, 0)
    assert miserlymouse.clock.seconds_until("3pm", now) == 6 * 3600


def test_wraps_to_tomorrow() -> None:
    now = local(2026, 8, 27, 16, 0)
    assert miserlymouse.clock.seconds_until("3pm", now) == 23 * 3600


def test_same_time_wraps_a_full_day() -> None:
    now = local(2026, 8, 27, 15, 0)
    assert miserlymouse.clock.seconds_until("3pm", now) == 24 * 3600


def test_never_exceeds_a_day() -> None:
    now = local(2026, 8, 27, 9, 17)
    for hour in range(24):
        seconds = miserlymouse.clock.seconds_until(f"{hour:02d}00", now)
        assert 0 < seconds <= 24 * 3600
