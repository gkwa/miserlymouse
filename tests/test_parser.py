import pytest

import miserlymouse.parser


@pytest.mark.parametrize(
    "argv,expected",
    [
        (["2h"], ["for", "2h"]),
        (["2h", "make", "build"], ["for", "2h", "make", "build"]),
        (["--dry-run", "2h"], ["--dry-run", "for", "2h"]),
        (["for", "2h"], ["for", "2h"]),
        (["until", "3pm"], ["until", "3pm"]),
        (["--dry-run", "until", "3pm"], ["--dry-run", "until", "3pm"]),
        (["--version"], ["--version"]),
        ([], []),
    ],
)
def test_normalize(argv: list[str], expected: list[str]) -> None:
    assert miserlymouse.parser.normalize(argv) == expected


def parse(argv: list[str]):
    parser = miserlymouse.parser.build_parser()
    return parser.parse_args(miserlymouse.parser.normalize(argv))


def test_bare_duration_selects_for() -> None:
    options = parse(["2h"])
    assert options.command == "for"
    assert options.duration == "2h"


def test_until_keeps_utility_intact() -> None:
    options = parse(["until", "3pm", "make", "build"])
    assert options.command == "until"
    assert options.time == "3pm"
    assert options.utility == ["make", "build"]


def test_flag_before_subcommand_survives() -> None:
    options = parse(["--dry-run", "until", "3pm"])
    assert options.dry_run is True


def test_flag_between_subcommand_and_argument_survives() -> None:
    options = parse(["until", "--dry-run", "3pm"])
    assert options.dry_run is True


def test_flags_after_the_argument_belong_to_the_utility() -> None:
    options = parse(["for", "30m", "make", "--jobs", "4"])
    assert options.utility == ["make", "--jobs", "4"]
    assert not hasattr(options, "dry_run")


@pytest.mark.parametrize(
    "utility,expected",
    [
        (["make", "build"], None),
        (["--json"], "--json"),
        (["-d"], "-d"),
        ([], None),
    ],
)
def test_stray_option(utility: list[str], expected: str | None) -> None:
    assert miserlymouse.parser.stray_option(utility, False) == expected


def test_double_dash_escapes_the_guard() -> None:
    utility, escaped = miserlymouse.parser.split_utility(["--", "--weird-binary"])
    assert utility == ["--weird-binary"]
    assert escaped is True
    assert miserlymouse.parser.stray_option(utility, escaped) is None


def test_without_double_dash_the_guard_fires() -> None:
    utility, escaped = miserlymouse.parser.split_utility(["--weird-binary"])
    assert escaped is False
    assert miserlymouse.parser.stray_option(utility, escaped) == "--weird-binary"
