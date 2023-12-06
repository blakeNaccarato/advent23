"""Tests for the Advent of Code 2023."""

from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from advent23 import get_ex_inp
from advent23_tests.answers import CHECKS
from advent23_tests.namespaces import get_cached_nb_ns

COMPARE_USER = "blake"
"""User to compare against."""

INPUT = Path("input")
"""Input directory."""
PACKAGE = Path("src/advent23")
"""Package to test."""

EXAMPLES = {"ex_a": "ans_a", "ex_b": "ans_b"}
DEFAULT_EXPECTED = dict(zip(EXAMPLES.values(), [None] * len(EXAMPLES), strict=True))


@dataclass
class Case:
    """Puzzle test case."""

    user: str
    day: str
    check: str
    other_user: str | None = None
    compare: bool = False
    compare_pos: str = ""

    @property
    def answer(s):
        """Given answer."""
        chk = getattr(s.ns, "chk", None)
        return chk.get(s.check) if chk else None

    @property
    def expected(s):
        """Expected answer."""
        if s.compare and (other_case := s.other_case):
            return other_case.answer
        return get_expectations(s.day, s.user, s.other_user).get(s.check)

    @property
    def inp(s) -> str:
        """Test input."""
        user = s.other_user or s.user
        path = INPUT / user / f"{s.day}.txt"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @property
    def ns(s) -> SimpleNamespace:
        """Notebook namespace."""
        if s.other_user in EXAMPLES:
            params = {"inp": {part: get_ex_inp(s.day, part) for part in ("a", "b")}}
        else:
            params = {"inp": {part: s.inp for part in ("a", "b")}}
        return get_cached_nb_ns(nb=s.nb, params=params)

    @property
    def nb(s) -> str:
        path = PACKAGE / s.user / f"day{s.day}.ipynb"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @property
    def isolated_case(s):
        """The case for just this user."""
        return Case(**(asdict(s) | dict(other_user=None, compare=False)))

    @property
    def other_case(s):
        """The case for the other user."""
        return (
            Case(**(asdict(s) | dict(user=s.other_user, compare=False)))
            if s.other_user
            else None
        )

    @property
    def basic_case(s):
        """The basic case."""
        return Case(**(asdict(s) | dict(other_user="ex_a", compare=False)))

    @property
    def id(s) -> str:  # noqa: A003
        """Get test ID."""
        return "_".join([e for e in (s.compare_pos, s.check) if e])

    @property
    def marks(s) -> tuple[pytest.MarkDecorator, ...]:
        """Test marks."""
        return (
            *(
                pytest.mark.skipif(cond, reason=f"{s.id}: {reason}")
                for reason, cond in {
                    "No notebook": not s.nb,
                    "No input": not s.inp or not s.isolated_case.inp,
                    "Not attempted": s.check not in s.basic_case.ns.chk,
                    "Not answered": s.other_user is not None and not s.expected,
                }.items()
            ),
            *(
                pytest.mark.xfail(
                    cond, reason=f"{s.id}: {reason}", raises=AssertionError
                )
                for reason, cond in {
                    "Not answered": s.other_user is None and not s.expected,
                    "Check not answered": (
                        s.other_user is not None
                        and not s.compare
                        and s.other_user not in EXAMPLES
                        and not s.isolated_case.expected
                    ),
                }.items()
            ),
        )


def get_expectations(
    day: str, user: str, other_user: str | None = None
) -> dict[str, Any]:
    """Expected answers."""
    return CHECKS[day][other_user or user]


def parametrize(user: str, day: str, others: bool = False):
    """Parametrize cases by user, day, other user, and whether to run checks."""
    return pytest.mark.parametrize(
        ("ans", "exp"),
        [
            pytest.param(*(case, case), id=case.id, marks=case.marks)
            for case in get_cases(user, day, others)
        ],
        indirect=True,
    )


def get_cases(user: str, day: str, others: bool) -> Iterator[Case]:
    for other_user in sorted(set(CHECKS["01"]) - {user}) if others else (None,):
        for check in get_expectations(day, user, other_user):
            if any(other_user == ex and check != ans for ex, ans in EXAMPLES.items()):
                continue
            yield Case(user, day, check, other_user)


def parametrize_compare(user: str, other_user: str, day: str):
    """Parametrize cases by user, day, other user, and whether to run checks."""
    return pytest.mark.parametrize(
        ("ans", "exp"),
        [
            pytest.param(*(case, case), id=case.id, marks=case.marks)
            for case in get_cases_compare(user, other_user, day)
        ],
        indirect=True,
    )


def get_cases_compare(user: str, other_user: str, day: str) -> Iterator[Case]:
    user_checks = Case(user, day, "").ns.chk.keys()
    other_user_checks = Case(other_user, day, "").ns.chk.keys()
    for i, check in enumerate(c for c in other_user_checks if c in user_checks):
        yield Case(user, day, check, other_user, True, compare_pos=str(i).zfill(2))
