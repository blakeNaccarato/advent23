"""Test helpers."""

from typing import Any, NamedTuple

from advent23_tests.answers import ANSWERS


class Args(NamedTuple):
    """Indirect parameters for fixtures."""

    user: str
    day: str
    basic: bool = False


class Exp(NamedTuple):
    """Expected answer."""

    basic: Any
    full: Any


ANSWERS = {day: Exp(*ans) for day, ans in ANSWERS.items()}


def get_ans(day: str, basic: bool = False) -> Any:
    """Get expected answer."""
    return ANSWERS[day].basic if basic else ANSWERS[day].full
