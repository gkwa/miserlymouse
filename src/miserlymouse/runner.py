import logging
import shutil
import subprocess
import sys
import time
import typing

import miserlymouse.progress

CAFFEINATE = "caffeinate"
INTERRUPTED = 130
GRACE_SECONDS = 5

ASSERTIONS: tuple[tuple[str, str], ...] = (
    ("display", "-d"),
    ("idle", "-i"),
    ("disk", "-m"),
    ("system", "-s"),
    ("user_active", "-u"),
)


class Warner(typing.Protocol):
    """Whatever wants telling how many seconds of assertion are left."""

    def check(self, remaining: int) -> None: ...


def build_command(
    seconds: int,
    flags: typing.Mapping[str, bool],
    utility: typing.Sequence[str],
) -> list[str]:
    command = [CAFFEINATE]
    command.extend(option for name, option in ASSERTIONS if flags.get(name))
    command.extend(["-t", str(seconds)])
    command.extend(utility)
    return command


def resolve() -> str:
    path = shutil.which(CAFFEINATE)
    if path is None:
        raise FileNotFoundError(f"{CAFFEINATE} not found on PATH")
    return path


def exit_code(returncode: int) -> int:
    if returncode < 0:
        return 128 - returncode
    return returncode


def supervise(
    command: typing.Sequence[str],
    seconds: int,
    show_progress: bool,
    stream: typing.TextIO | None = None,
    warner: Warner | None = None,
) -> int:
    target = stream if stream is not None else sys.stderr
    logging.debug("spawn %s", " ".join(command))
    process = subprocess.Popen(list(command))
    started = time.monotonic()
    try:
        wait(process, seconds, started, show_progress, target, warner)
    except KeyboardInterrupt:
        stop(process)
        erase(target, show_progress)
        return INTERRUPTED
    erase(target, show_progress)
    return exit_code(process.returncode)


def wait(
    process: subprocess.Popen,
    seconds: int,
    started: float,
    show_progress: bool,
    stream: typing.TextIO,
    warner: Warner | None = None,
) -> None:
    while True:
        try:
            process.wait(timeout=miserlymouse.progress.INTERVAL)
            return
        except subprocess.TimeoutExpired:
            elapsed = time.monotonic() - started
            if warner is not None:
                warner.check(max(seconds - int(elapsed), 0))
            if show_progress:
                draw(stream, seconds, elapsed)


def draw(stream: typing.TextIO, seconds: int, elapsed: float) -> None:
    columns = shutil.get_terminal_size().columns
    stream.write("\r" + miserlymouse.progress.render(int(elapsed), seconds, columns))
    stream.flush()


def erase(stream: typing.TextIO, show_progress: bool) -> None:
    if not show_progress:
        return
    columns = shutil.get_terminal_size().columns
    stream.write("\r" + " " * columns + "\r")
    stream.flush()


def stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
