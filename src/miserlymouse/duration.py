import re

UNIT_SECONDS: dict[str, int] = {
    "w": 604800,
    "d": 86400,
    "h": 3600,
    "m": 60,
    "s": 1,
}

NUMBER = re.compile(r"\d+(?:\.\d+)?|\.\d+")
UNIT_TOKEN = re.compile(r"\s*(?P<value>\d+(?:\.\d+)?|\.\d+)\s*(?P<unit>[wdhms])\s*")


class DurationError(ValueError):
    pass


def parse_duration(text: str) -> int:
    stripped = text.strip().lower()
    if not stripped:
        raise DurationError("duration is empty")
    if ":" in stripped:
        return finalize(parse_clock(stripped, text))
    if NUMBER.fullmatch(stripped):
        return finalize(float(stripped))
    return finalize(parse_units(stripped, text))


def parse_clock(stripped: str, original: str) -> float:
    fields = stripped.split(":")
    if len(fields) not in (2, 3):
        raise DurationError(f"cannot parse duration: {original!r}")
    if not all(NUMBER.fullmatch(field) for field in fields):
        raise DurationError(f"cannot parse duration: {original!r}")
    scales = (3600, 60, 1) if len(fields) == 3 else (3600, 60)
    return sum(float(field) * scale for field, scale in zip(fields, scales))


def parse_units(stripped: str, original: str) -> float:
    total = 0.0
    position = 0
    for match in UNIT_TOKEN.finditer(stripped):
        if match.start() != position:
            raise DurationError(f"cannot parse duration: {original!r}")
        total += float(match.group("value")) * UNIT_SECONDS[match.group("unit")]
        position = match.end()
    if position != len(stripped):
        raise DurationError(f"cannot parse duration: {original!r}")
    return total


def finalize(total: float) -> int:
    seconds = int(round(total))
    if seconds <= 0:
        raise DurationError("duration must be greater than zero")
    return seconds
