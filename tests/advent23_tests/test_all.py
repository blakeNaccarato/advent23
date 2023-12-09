"""Test configuration."""

import pytest

from advent23_tests.attempts import Attempt, get_attempts


@pytest.mark.parametrize(
    ("att", "check"),
    (
        pytest.param(attempt, check, id=attempt.get_id(check))
        for attempt in get_attempts()
        for check in attempt.checks
    ),
)
def test_example(att: Attempt, check: str):
    assert att.get_answer(check) == att.get_expected_answer(check)


@pytest.mark.parametrize(
    ("att", "check"),
    (
        pytest.param(attempt, check, id=attempt.get_id(check, str(i).zfill(2)))
        for attempt in get_attempts("blake")
        for i, check in enumerate(attempt.checks)
        if attempt.user != "blake"
    ),
)
def test_compare_to_blake(att: Attempt, check: str):
    assert att.get_answer(check) == att.get_expected_answer(check)
