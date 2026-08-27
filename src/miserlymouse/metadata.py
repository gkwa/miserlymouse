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
    }


def render(record: typing.Mapping[str, typing.Any]) -> str:
    return json.dumps(record, indent=2)
