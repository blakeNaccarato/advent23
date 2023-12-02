"""Tests for the Advent of Code 2023."""

from dataclasses import dataclass
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal, TypeAlias

import pytest
from boilercore.hashes import hash_args
from boilercore.notebooks.namespaces import get_nb_ns
from cachier import cachier

from advent23_tests.answers import ANSWERS

INPUT = Path("input")
"""Input directory."""
PACKAGE = Path("src/advent23")
"""Package to test."""

Part: TypeAlias = Literal["a", "b"]
"""Puzzle part."""
Params: TypeAlias = dict[str, Any]
"""Notebook parameters."""

NO_PARAMS = {}
"""No notebook parameters."""


@cachier(hash_func=partial(hash_args, get_nb_ns))
def get_cached_nb_ns(nb: str, params: Params = NO_PARAMS) -> SimpleNamespace:
    """Get cached minimal namespace suitable for passing to a receiving function."""
    return get_nb_ns(nb, params)


@dataclass
class Case:
    """Puzzle test case."""

    user: str
    day: str
    part: Part
    reverse: bool = False
    user_for_input: str | None = None

    @property
    def marks(s) -> pytest.MarkDecorator | tuple[pytest.MarkDecorator, ...]:
        return pytest.mark.xfail if s.expected is None else ()

    @property
    def ns(s) -> SimpleNamespace:
        """Namespace."""
        ns = get_cached_nb_ns(nb=s.nb, params={"INPUT_A": s.inp, "INPUT_B": s.inp})
        ns.ANS = getattr(ns, f"ANS_{s.part.upper()}")
        return ns

    @property
    def nb(s) -> str:
        """Notebook."""
        return (PACKAGE / s.user / f"day{s.day}.ipynb").read_text(encoding="utf-8")

    @property
    def inp(s) -> str:
        """Test input."""
        user = s.user_for_input or s.user
        return (INPUT / user / f"day{s.day}.txt").read_text(encoding="utf-8")

    @property
    def expected(s):
        """Expected answer."""
        answers = ANSWERS[s.day][s.user]
        answers = tuple(reversed(answers)) if s.reverse else answers
        return answers[0] if s.part == "a" else answers[1]


def parametrize(user: str, day: str, reverse: bool = False):
    """Parametrize cases by user and day."""
    return pytest.mark.parametrize(
        ("ns", "expected"),
        [
            pytest.param(c, c, id=f"{c.part}", marks=c.marks)
            for c in (
                Case(user, day, part, reverse)  # type: ignore
                for part in (["a"] if reverse else ["a", "b"])
            )
        ],
        indirect=True,
    )
