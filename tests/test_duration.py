import pytest

import miserlymouse.duration


@pytest.mark.parametrize(
    "text,expected",
    [
        ("7200", 7200),
        ("2h", 7200),
        ("30m", 1800),
        ("1h24m", 5040),
        ("1h 24m", 5040),
        ("1H24M", 5040),
        ("1h30m10s", 5410),
        ("1.5h", 5400),
        (".5h", 1800),
        ("90s", 90),
        ("1d", 86400),
        ("1w", 604800),
        ("1d2h3m4s", 93784),
        ("1:24", 5040),
        ("1:24:30", 5070),
        ("0:90", 5400),
        ("  2h  ", 7200),
    ],
)
def test_parses(text: str, expected: int) -> None:
    assert miserlymouse.duration.parse_duration(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "abc",
        "2hours",
        "2x",
        "h",
        "-5m",
        "0",
        "0s",
        "1:2:3:4",
        "1:",
        "2h junk",
    ],
)
def test_rejects(text: str) -> None:
    with pytest.raises(miserlymouse.duration.DurationError):
        miserlymouse.duration.parse_duration(text)
