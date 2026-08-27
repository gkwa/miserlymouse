import logging
import sys

LEVELS: tuple[int, ...] = (logging.WARNING, logging.INFO, logging.DEBUG)


def configure(verbosity: int) -> None:
    level = LEVELS[min(verbosity, len(LEVELS) - 1)]
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(levelname)s %(message)s",
    )
