import argparse
import importlib.metadata
import shlex
import sys
import typing

import miserlymouse.duration
import miserlymouse.logging_setup
import miserlymouse.runner

EPILOG = (
    """durations accept 2h, 30m, 1h24m, 1.5h, 90s, 1d, 1:24, 1:24:30, or bare seconds"""
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="miserlymouse",
        description="Run caffeinate for a human-readable duration",
        epilog=EPILOG,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('miserlymouse')}",
    )
    parser.add_argument(
        "--display", "-d", action="store_true", help="keep the display awake"
    )
    parser.add_argument("--idle", "-i", action="store_true", help="prevent idle sleep")
    parser.add_argument(
        "--disk", "-m", action="store_true", help="prevent disk idle sleep"
    )
    parser.add_argument(
        "--system", "-s", action="store_true", help="prevent system sleep on AC"
    )
    parser.add_argument(
        "--user-active", "-u", action="store_true", help="declare the user active"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the caffeinate command instead of running it",
    )
    parser.add_argument(
        "--verbose", "-v", action="count", default=0, help="raise the log level"
    )
    parser.add_argument("duration", help="how long to stay awake, such as 1h24m")
    parser.add_argument(
        "utility",
        nargs=argparse.REMAINDER,
        help="optional command to run while awake",
    )
    return parser


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = build_parser()
    options = parser.parse_args(argv)
    miserlymouse.logging_setup.configure(options.verbose)

    try:
        seconds = miserlymouse.duration.parse_duration(options.duration)
    except miserlymouse.duration.DurationError as error:
        parser.error(str(error))

    command = miserlymouse.runner.build_command(seconds, vars(options), options.utility)
    if options.dry_run:
        print(shlex.join(command))
        return 0

    try:
        miserlymouse.runner.resolve()
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1

    miserlymouse.runner.run(command)
