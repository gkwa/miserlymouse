import pytest

import miserlymouse.progress
import miserlymouse.runner


@pytest.mark.parametrize(
    "elapsed,total,expected",
    [(0, 100, 0), (50, 100, 50), (100, 100, 100), (150, 100, 100), (5, 0, 100)],
)
def test_percent(elapsed: int, total: int, expected: int) -> None:
    assert miserlymouse.progress.percent(elapsed, total) == expected


def test_bar_fills_proportionally() -> None:
    assert miserlymouse.progress.bar(5, 10, 10) == "█████░░░░░"


def test_bar_never_overflows() -> None:
    assert len(miserlymouse.progress.bar(999, 10, 10)) == 10


def test_render_fits_the_terminal() -> None:
    line = miserlymouse.progress.render(30, 60, 80)
    assert len(line) <= 80
    assert "50%" in line
    assert "30s left" in line


def test_render_survives_a_narrow_terminal() -> None:
    line = miserlymouse.progress.render(30, 60, 10)
    assert "50%" in line


def test_left_reads_done_at_the_end() -> None:
    assert miserlymouse.progress.left(0) == "done"


@pytest.mark.parametrize("returncode,expected", [(0, 0), (1, 1), (-2, 130), (-15, 143)])
def test_exit_code(returncode: int, expected: int) -> None:
    assert miserlymouse.runner.exit_code(returncode) == expected
