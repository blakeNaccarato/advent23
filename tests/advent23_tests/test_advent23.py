"""Tests for user attempts of Advent of Code 2023 challenges."""

import pytest

from advent23_tests.attempts import Attempt, walk_attempts


@pytest.mark.parametrize(
    ("att", "check"),
    (
        pytest.param(attempt, check, id=attempt.get_id(check))
        for attempt in walk_attempts()
        for check in attempt.checks
    ),
)
def test_example(att: Attempt, check: str):
    """Test attempts against examples and their answers in `input/examples.toml`."""
    assert att.get_answer(check) == att.get_expected_answer(check)
