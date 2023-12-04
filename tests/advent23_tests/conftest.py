"""Test configuration."""

import pytest

from advent23_tests import Case, Check


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    case: Case | Check = request.param  # type: ignore
    return case.answer


@pytest.fixture()
def exp(request):
    """Expected answer."""
    case: Case | Check = request.param  # type: ignore
    return case.expected
