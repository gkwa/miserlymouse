import miserlymouse.duration

FILLED = "█"
EMPTY = "░"
MINIMUM_WIDTH = 10
INTERVAL = 0.25


def render(elapsed: int, total: int, columns: int) -> str:
    remaining = max(total - elapsed, 0)
    suffix = f" {percent(elapsed, total):3d}% {left(remaining)}"
    width = max(MINIMUM_WIDTH, columns - len(suffix) - 1)
    return bar(elapsed, total, width) + suffix


def percent(elapsed: int, total: int) -> int:
    if total <= 0:
        return 100
    return min(int(elapsed * 100 / total), 100)


def left(remaining: int) -> str:
    if remaining <= 0:
        return "done"
    return f"{miserlymouse.duration.format_duration(remaining)} left"


def bar(elapsed: int, total: int, width: int) -> str:
    if total <= 0:
        return FILLED * width
    filled = min(int(width * elapsed / total), width)
    return FILLED * filled + EMPTY * (width - filled)
