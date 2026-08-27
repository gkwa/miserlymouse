import argparse
import datetime
import shlex
import sys
import typing

import miserlymouse.clock
import miserlymouse.duration
import miserlymouse.logging_setup
import miserlymouse.metadata
import miserlymouse.parser
import miserlymouse.runner


def json_stream(utility: typing.Sequence[str], dry_run: bool) -> typing.TextIO:
    """Keep the record off stdout only where a wrapped command will claim it."""
    if utility and not dry_run:
        return sys.stderr
    return sys.stdout


def wants_progress(options: argparse.Namespace, utility: typing.Sequence[str]) -> bool:
    """A wrapped command owns the terminal, and a pipe has nobody watching."""
    if getattr(options, "no_progress", False):
        return False
    if utility:
        return False
    return sys.stderr.isatty()


def resolve_seconds(
    options: argparse.Namespace, now: datetime.datetime
) -> tuple[str, int]:
    if options.command == "until":
        return options.time, miserlymouse.clock.seconds_until(options.time, now)
    return options.duration, miserlymouse.duration.parse_duration(options.duration)


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = miserlymouse.parser.build_parser()
    tokens = list(sys.argv[1:] if argv is None else argv)
    options = parser.parse_args(miserlymouse.parser.normalize(tokens))
    miserlymouse.logging_setup.configure(getattr(options, "verbose", 0))

    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    try:
        request, seconds = resolve_seconds(options, now)
    except (miserlymouse.duration.DurationError, miserlymouse.clock.TimeError) as error:
        parser.error(str(error))

    utility, escaped = miserlymouse.parser.split_utility(options.utility)
    stray = miserlymouse.parser.stray_option(utility, escaped)
    if stray is not None:
        parser.error(
            f"unrecognized option {stray}, "
            f"options belong before the {options.command} argument"
        )

    flags = {
        name: getattr(options, name, False) for name in miserlymouse.parser.FLAG_NAMES
    }
    command = miserlymouse.runner.build_command(seconds, flags, utility)

    wants_json = getattr(options, "json", False)
    dry_run = getattr(options, "dry_run", False)
    if wants_json:
        record = miserlymouse.metadata.build(
            options.command, request, seconds, now, command
        )
        print(
            miserlymouse.metadata.render(record),
            file=json_stream(utility, dry_run),
        )

    if dry_run:
        if not wants_json:
            print(shlex.join(command))
        return 0

    try:
        miserlymouse.runner.resolve()
    except FileNotFoundError as error:
        print(str(error), file=sys.stderr)
        return 1

    return miserlymouse.runner.supervise(
        command, seconds, wants_progress(options, utility)
    )
