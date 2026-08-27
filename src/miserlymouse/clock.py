import datetime
import re

NAMED: dict[str, tuple[int, int]] = {
    "noon": (12, 0),
    "midnight": (0, 0),
}

MERIDIEM_FORMS: tuple[tuple[str, str], ...] = (
    ("a.m.", "am"),
    ("p.m.", "pm"),
    ("a.m", "am"),
    ("p.m", "pm"),
)

PATTERN = re.compile(
    r"^(?P<hour>\d{1,2})(?:[:.]?(?P<minute>\d{2}))?(?P<meridiem>am|pm)?$"
)


class TimeError(ValueError):
    pass


def normalize(text: str) -> str:
    compact = re.sub(r"\s+", "", text.strip().lower())
    for source, target in MERIDIEM_FORMS:
        compact = compact.replace(source, target)
    return compact


def parse_time(text: str) -> tuple[int, int]:
    compact = normalize(text)
    if not compact:
        raise TimeError("time is empty")
    if compact in NAMED:
        return NAMED[compact]

    match = PATTERN.fullmatch(compact)
    if match is None:
        raise TimeError(f"cannot parse time: {text!r}")

    minute_text = match.group("minute")
    meridiem = match.group("meridiem")
    if meridiem is None and minute_text is None:
        raise TimeError(f"ambiguous time: {text!r}, write 3pm or 15:00")

    hour = int(match.group("hour"))
    minute = int(minute_text) if minute_text is not None else 0
    if minute > 59:
        raise TimeError(f"minute out of range: {text!r}")
    if meridiem is None:
        return twenty_four_hour(hour, minute, text)
    return twelve_hour(hour, minute, meridiem, text)


def twenty_four_hour(hour: int, minute: int, text: str) -> tuple[int, int]:
    if hour > 23:
        raise TimeError(f"hour out of range: {text!r}")
    return hour, minute


def twelve_hour(hour: int, minute: int, meridiem: str, text: str) -> tuple[int, int]:
    if not 1 <= hour <= 12:
        raise TimeError(f"hour out of range: {text!r}")
    if meridiem == "am":
        return (0 if hour == 12 else hour), minute
    return (12 if hour == 12 else hour + 12), minute


def next_occurrence(
    hour: int, minute: int, now: datetime.datetime
) -> datetime.datetime:
    local = now.replace(tzinfo=None)
    target = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= local:
        target += datetime.timedelta(days=1)
    return target.astimezone()


def seconds_until(text: str, now: datetime.datetime) -> int:
    hour, minute = parse_time(text)
    target = next_occurrence(hour, minute, now)
    seconds = int(round((target - now).total_seconds()))
    if seconds <= 0:
        raise TimeError(f"time is not in the future: {text!r}")
    return seconds
