from collections.abc import Iterator

import pytest

from advent23 import EXAMPLES, PARTS
from advent23_tests.cases import Attempt, Case

USERS = ("blake", "abdul", "brad")
"""Users to test."""
OTHER = "blake"
"""User to compare against."""


def parametrize(params):
    """Test parametrization specific to this module."""
    return pytest.mark.parametrize(("ans", "exp"), params, indirect=True)


def get_attempts(other: str = "") -> Iterator[Attempt]:
    for day in EXAMPLES:
        attempts = (
            Attempt(user, day, Attempt(other, day) if other else None) for user in USERS
        )
        yield from (
            att
            for att in attempts
            if att.nb and att.inp
            if other and att.user != other or not other
        )


@parametrize(
    pytest.param(*([Case(attempt, answer)] * 2), id=attempt.get_id(answer))
    for attempt in get_attempts()
    for answer in PARTS
)
def test_example(ans, exp):
    assert ans == exp


@parametrize(
    pytest.param(
        *([Case(attempt, check)] * 2), id=attempt.get_id(check, str(i).zfill(2))
    )
    for attempt in get_attempts(OTHER)
    for i, check in enumerate(attempt.checks)
    if attempt.user != OTHER
)
def test_compare(ans, exp):
    assert ans == exp
