"""Test configuration."""

from unittest.mock import _SentinelObject  # type: ignore

import pytest

from advent23_tests.cases import Case


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    attempt, check = Case(*request.param)
    return attempt.get_answer(check) or _SentinelObject("ans")


@pytest.fixture()
def exp(request):
    """Expected answer."""
    attempt, check = Case(*request.param)
    return attempt.get_expected_answer(check) or _SentinelObject("exp")
