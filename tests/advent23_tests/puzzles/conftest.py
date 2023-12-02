"""Test configuration for user-specific puzzle answers."""

from types import SimpleNamespace

import pytest

from advent23_tests import get_ns
from advent23_tests.puzzles import get_ans, get_input


@pytest.fixture()
def ns(request) -> SimpleNamespace:
    """Puzzle namespace."""
    args = request.param
    day, user, part = args
    return get_ns(day, user, part, get_input(day, user))


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    args = request.param
    day, user, part = args
    return get_ans(day, user, part)
