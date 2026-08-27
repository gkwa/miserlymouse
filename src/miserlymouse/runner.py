import logging
import os
import shutil
import typing

CAFFEINATE = "caffeinate"

ASSERTIONS: tuple[tuple[str, str], ...] = (
    ("display", "-d"),
    ("idle", "-i"),
    ("disk", "-m"),
    ("system", "-s"),
    ("user_active", "-u"),
)


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


def run(command: typing.Sequence[str]) -> typing.NoReturn:
    logging.debug("exec %s", " ".join(command))
    os.execvp(command[0], list(command))


def resolve() -> str:
    path = shutil.which(CAFFEINATE)
    if path is None:
        raise FileNotFoundError(f"{CAFFEINATE} not found on PATH")
    return path
