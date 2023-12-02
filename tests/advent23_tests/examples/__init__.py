"""Tests for examples given in the prompts."""

from typing import Any, Literal, TypeAlias

from advent23_tests import INPUT
from advent23_tests.answers import BASIC_ANSWERS

Part: TypeAlias = Literal["a", "b"]


def get_ans(day: str, part: Part) -> Any:
    """Get expected answer."""
    return BASIC_ANSWERS[day][part]


def get_input(day: str, part: Part) -> str:
    """Get test input."""
    return (
        (INPUT / "_example" / f"day{day}{part}")
        .with_suffix(".txt")
        .read_text(encoding="utf-8")
    )
