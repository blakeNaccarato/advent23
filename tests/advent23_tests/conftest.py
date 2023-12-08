"""Test configuration."""

from unittest.mock import _SentinelObject  # type: ignore

import pytest

from advent23_tests import Case  # type: ignore


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    attempt, check, other = Case(*request.param)
    return attempt.answer(check, other) or _SentinelObject("ans")


@pytest.fixture()
def exp(request):
    """Expected answer."""
    foo: Case = request.param
    attempt, check, other = foo
    return attempt.expected(check, other) or _SentinelObject("exp")
