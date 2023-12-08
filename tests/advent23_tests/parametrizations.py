"""Parametrizations."""

from collections.abc import Iterator

import pytest
from _pytest.mark.structures import ParameterSet

from advent23_tests import DAYS, EXAMPLES, OTHER, USERS
from advent23_tests.cases import Attempt, Case


def parametrize(walker):
    return pytest.mark.parametrize(("ans", "exp"), start(walker), indirect=True)


def start(walker) -> Iterator[ParameterSet]:
    for day in DAYS:
        for user in USERS:
            attempt = Attempt(user, day)
            if not attempt.nb:
                continue
            yield from walker(attempt)


def walk_self(attempt: Attempt) -> Iterator[ParameterSet]:
    yield from (
        pytest.param(
            *([Case(attempt, check)] * 2),
            id=attempt.get_id(check),
            marks=attempt.marks(check),
        )
        for check in attempt.checks
        if check in EXAMPLES.values()
    )


def walk_other(attempt: Attempt) -> Iterator[ParameterSet]:
    """Parametrize cases by user and day."""
    if attempt.user == OTHER:
        return
    other = Attempt(OTHER, attempt.day)
    checks = {
        c: str(i).zfill(2)
        for i, c in enumerate(c for c in attempt.checks if c in other.checks)
    }
    yield from (
        pytest.param(
            *([Case(attempt, check, other)] * 2),
            id=attempt.get_id(check, i),
            marks=attempt.marks(check, other),
        )
        for check, i in checks.items()
    )


def walk_ex(attempt: Attempt) -> Iterator[ParameterSet]:
    yield from (
        pytest.param(
            *([Case(attempt, check, ex)] * 2),
            id=attempt.get_id(check),
            marks=attempt.marks(check, ex),
        )
        for check, ex in {
            check: Attempt(ex, attempt.day) for ex, check in EXAMPLES.items()
        }.items()
        if ex.expected(check)
    )
