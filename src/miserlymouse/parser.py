import argparse
import importlib.metadata

import miserlymouse.duration
import miserlymouse.notify

COMMANDS: tuple[str, ...] = ("for", "until")

VALUE_OPTIONS: frozenset[str] = frozenset({"--warn", "--topic"})

FLAG_NAMES: tuple[str, ...] = ("display", "idle", "disk", "system", "user_active")

DURATION_HELP = "2h, 30m, 1h24m, 1.5h, 90s, 1d, 1:24, 1:24:30, or bare seconds"
TIME_HELP = "3pm, 12.15pm, 12:15pm, 1215pm, 15:00, 1500, noon, or midnight"

WARN_DEFAULT = ",".join(
    miserlymouse.duration.format_duration(offset)
    for offset in miserlymouse.notify.DEFAULT_WARNINGS
)


def normalize(argv: list[str]) -> list[str]:
    """Insert the implicit for, without mistaking an option's value for it."""
    skip = False
    for index, token in enumerate(argv):
        if skip:
            skip = False
            continue
        if token.startswith("-"):
            skip = token in VALUE_OPTIONS
            continue
        if token in COMMANDS:
            return argv
        return argv[:index] + ["for"] + argv[index:]
    return argv


def build_common() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    hidden = argparse.SUPPRESS
    common.add_argument(
        "--display",
        "-d",
        action="store_true",
        default=hidden,
        help="keep the display awake",
    )
    common.add_argument(
        "--idle",
        "-i",
        action="store_true",
        default=hidden,
        help="prevent idle sleep",
    )
    common.add_argument(
        "--disk",
        "-m",
        action="store_true",
        default=hidden,
        help="prevent disk idle sleep",
    )
    common.add_argument(
        "--system",
        "-s",
        action="store_true",
        default=hidden,
        help="prevent system sleep on AC",
    )
    common.add_argument(
        "--user-active",
        "-u",
        action="store_true",
        default=hidden,
        help="declare the user active",
    )
    common.add_argument(
        "--json",
        action="store_true",
        default=hidden,
        help="print a JSON record of the schedule to stdout",
    )
    common.add_argument(
        "--warn",
        metavar="OFFSETS",
        default=hidden,
        help=f"push ntfy warnings this long before the end (default: {WARN_DEFAULT})",
    )
    common.add_argument(
        "--topic",
        default=hidden,
        help=f"ntfy topic to push to (default: {miserlymouse.notify.DEFAULT_TOPIC})",
    )
    common.add_argument(
        "--no-notify",
        action="store_true",
        default=hidden,
        help="push no ntfy warnings at all",
    )
    common.add_argument(
        "--no-progress",
        action="store_true",
        default=hidden,
        help="never draw the progress bar",
    )
    common.add_argument(
        "--dry-run",
        action="store_true",
        default=hidden,
        help="print the caffeinate command instead of running it",
    )
    common.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=hidden,
        help="raise the log level",
    )
    return common


def build_parser() -> argparse.ArgumentParser:
    common = build_common()
    parser = argparse.ArgumentParser(
        prog="miserlymouse",
        parents=[common],
        description="Run caffeinate for a human duration or until a clock time",
        epilog="a bare duration is shorthand for the for subcommand",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {importlib.metadata.version('miserlymouse')}",
    )

    commands = parser.add_subparsers(dest="command", required=True)
    add_for(commands, common)
    add_until(commands, common)
    return parser


def add_for(commands: argparse._SubParsersAction, common) -> None:
    subparser = commands.add_parser(
        "for", parents=[common], help="stay awake for a duration"
    )
    subparser.add_argument("duration", help=DURATION_HELP)
    subparser.add_argument(
        "utility", nargs=argparse.REMAINDER, help="optional command to run while awake"
    )


def add_until(commands: argparse._SubParsersAction, common) -> None:
    subparser = commands.add_parser(
        "until", parents=[common], help="stay awake until the next such clock time"
    )
    subparser.add_argument("time", help=TIME_HELP)
    subparser.add_argument(
        "utility", nargs=argparse.REMAINDER, help="optional command to run while awake"
    )


def split_utility(utility: list[str]) -> tuple[list[str], bool]:
    """Return the utility words and whether a leading -- waived option checking."""
    if utility and utility[0] == "--":
        return utility[1:], True
    return utility, False


def stray_option(utility: list[str], escaped: bool) -> str | None:
    if escaped:
        return None
    if utility and utility[0].startswith("-"):
        return utility[0]
    return None
