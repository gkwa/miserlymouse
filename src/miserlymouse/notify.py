import datetime
import logging
import typing
import urllib.error
import urllib.request

import miserlymouse.duration

HOST = "https://ntfy.sh"
DEFAULT_TOPIC = "miserlymouse"
DEFAULT_WARNINGS: tuple[int, ...] = (3600, 1800, 300)
TIMEOUT = 10

STAGES: tuple[tuple[int, str], ...] = (
    (5, "rotating_light"),
    (4, "alarm_clock"),
    (3, "hourglass_flowing_sand"),
    (2, "sleeping"),
)


def stage(remaining: int) -> tuple[int, str]:
    """Escalate toward the end, counting back from the last warning of the run.

    Anchoring on the end rather than on the offset keeps the ladder meaningful
    for any --warn list, since the final warning is the urgent one whether it
    sits five minutes out or an hour.
    """
    return STAGES[min(remaining, len(STAGES) - 1)]


def parse_warnings(text: str) -> tuple[int, ...]:
    """Read a comma-separated list of durations, largest offset first."""
    fields = [field.strip() for field in text.split(",") if field.strip()]
    if not fields:
        raise miserlymouse.duration.DurationError("no warning offsets given")
    offsets = {miserlymouse.duration.parse_duration(field) for field in fields}
    return tuple(sorted(offsets, reverse=True))


def applicable(warnings: typing.Sequence[int], seconds: int) -> tuple[int, ...]:
    """Drop offsets that reach back past the start, which would fire at once."""
    return tuple(offset for offset in warnings if offset < seconds)


def clock(end: datetime.datetime, now: datetime.datetime) -> str:
    stamp = end.strftime("%-I:%M%p").lower()
    if end.date() == now.date():
        return stamp
    return f"{stamp} {end.strftime('%a')}"


def title(offset: int) -> str:
    return f"Mac sleeps in {miserlymouse.duration.format_duration(offset)}"


def body(end: datetime.datetime, now: datetime.datetime) -> str:
    return f"caffeinate drops the assertion at {clock(end, now)}"


def post(topic: str, headline: str, text: str, priority: int, tag: str) -> None:
    request = urllib.request.Request(
        f"{HOST}/{topic}",
        data=text.encode(),
        method="POST",
        headers={
            "Title": headline,
            "Priority": str(priority),
            "Tags": tag,
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        logging.debug("ntfy %s answered %s", topic, response.status)


class Notifier:
    """Pushes one ntfy warning as each offset before the end time is crossed."""

    def __init__(
        self,
        topic: str,
        warnings: typing.Sequence[int],
        end: datetime.datetime,
        now: datetime.datetime,
        sender: typing.Callable[[str, str, str, int, str], None] = post,
    ) -> None:
        self.topic = topic
        self.pending = sorted(warnings, reverse=True)
        self.end = end
        self.now = now
        self.sender = sender

    def check(self, remaining: int) -> None:
        due = [offset for offset in self.pending if remaining <= offset]
        if not due:
            return
        self.pending = [offset for offset in self.pending if offset not in due]
        self.fire(min(due))

    def fire(self, offset: int) -> None:
        """A failed push must never take the assertion down with it."""
        priority, tag = stage(len(self.pending))
        try:
            self.sender(
                self.topic,
                title(offset),
                body(self.end, self.now),
                priority,
                tag,
            )
        except (urllib.error.URLError, OSError) as error:
            logging.warning("ntfy warning at %s left unsent: %s", offset, error)
