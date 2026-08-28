import datetime
import json
import typing

import miserlymouse.duration


def build(
    mode: str,
    request: str,
    seconds: int,
    start: datetime.datetime,
    command: typing.Sequence[str],
    warnings: typing.Sequence[int] = (),
) -> dict[str, typing.Any]:
    end = start + datetime.timedelta(seconds=seconds)
    return {
        "mode": mode,
        "request": request,
        "seconds": seconds,
        "duration": miserlymouse.duration.format_duration(seconds),
        "start": start.isoformat(timespec="seconds"),
        "end": end.isoformat(timespec="seconds"),
        "timezone": start.tzname(),
        "command": list(command),
        "warnings": [warning(end, offset) for offset in warnings],
    }


def warning(end: datetime.datetime, offset: int) -> dict[str, typing.Any]:
    return {
        "offset": miserlymouse.duration.format_duration(offset),
        "at": (end - datetime.timedelta(seconds=offset)).isoformat(timespec="seconds"),
    }


def render(record: typing.Mapping[str, typing.Any]) -> str:
    return json.dumps(record, indent=2)
