import datetime
import urllib.error

import pytest

import miserlymouse.duration
import miserlymouse.notify


def stamp(hour: int, minute: int = 0, day: int = 28) -> datetime.datetime:
    return datetime.datetime(2026, 8, day, hour, minute)


class Recorder:
    def __init__(self, explode: bool = False) -> None:
        self.calls: list[tuple[str, str, str, bool]] = []
        self.explode = explode

    def __call__(self, topic: str, headline: str, text: str, urgent: bool) -> None:
        if self.explode:
            raise urllib.error.URLError("no route to host")
        self.calls.append((topic, headline, text, urgent))


def build(warnings: tuple[int, ...], sender: Recorder) -> miserlymouse.notify.Notifier:
    return miserlymouse.notify.Notifier(
        "topic", warnings, stamp(15, 30), stamp(13, 30), sender
    )


def test_parse_warnings_reads_durations_largest_first() -> None:
    assert miserlymouse.notify.parse_warnings("5m,30m,15m") == (1800, 900, 300)


def test_parse_warnings_collapses_duplicates() -> None:
    assert miserlymouse.notify.parse_warnings("5m, 300s") == (300,)


def test_parse_warnings_rejects_an_empty_list() -> None:
    with pytest.raises(miserlymouse.duration.DurationError):
        miserlymouse.notify.parse_warnings(" , ")


def test_applicable_drops_offsets_that_reach_past_the_start() -> None:
    assert miserlymouse.notify.applicable((1800, 900, 300), 1200) == (900, 300)


def test_applicable_drops_an_offset_equal_to_the_whole_span() -> None:
    assert miserlymouse.notify.applicable((1800,), 1800) == ()


def test_check_fires_once_as_each_offset_is_crossed() -> None:
    sender = Recorder()
    notifier = build((1800, 900, 300), sender)
    for remaining in (2000, 1801, 1800, 1799, 901, 900, 400, 300, 299, 1):
        notifier.check(remaining)
    assert [call[1] for call in sender.calls] == [
        "Mac sleeps in 30m",
        "Mac sleeps in 15m",
        "Mac sleeps in 5m",
    ]


def test_check_collapses_offsets_missed_in_one_tick() -> None:
    sender = Recorder()
    notifier = build((1800, 900, 300), sender)
    notifier.check(120)
    assert len(sender.calls) == 1
    assert sender.calls[0][1] == "Mac sleeps in 5m"


def test_the_last_warning_goes_out_urgent() -> None:
    sender = Recorder()
    notifier = build((1800, 300), sender)
    notifier.check(1800)
    notifier.check(300)
    assert [call[3] for call in sender.calls] == [False, True]


def test_body_names_the_end_time() -> None:
    assert miserlymouse.notify.body(stamp(15, 30), stamp(13, 30)) == (
        "caffeinate drops the assertion at 3:30pm"
    )


def test_body_names_the_weekday_when_the_end_is_another_day() -> None:
    assert "Sat" in miserlymouse.notify.body(stamp(15, 30, day=29), stamp(13, 30))


def test_a_failed_push_is_swallowed() -> None:
    notifier = build((300,), Recorder(explode=True))
    notifier.check(300)
    assert notifier.pending == []
