"""Tests for user-specific puzzle answers."""

from advent23_tests import INPUT, Part
from advent23_tests.answers import ANSWERS


def get_ans(day: str, user: str, part: Part):
    """Get expected answer."""
    answers = ANSWERS[day][user]
    return answers[0] if part == "a" else answers[1]


def get_input(day: str, user: str) -> str:
    """Get test input."""
    return (INPUT / user / f"day{day}").with_suffix(".txt").read_text(encoding="utf-8")
