"""Test configuration."""

from unittest.mock import _SentinelObject  # type: ignore

import pytest

from advent23_tests import Case


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    case: Case = request.param  # type: ignore
    return case.answer or _SentinelObject("ans")


@pytest.fixture()
def exp(request):
    """Expected answer."""
    case: Case = request.param  # type: ignore
    return case.expected or _SentinelObject("exp")
