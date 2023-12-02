"""Test configuration for  for examples given in the prompts."""

from types import SimpleNamespace

import pytest

from advent23_tests import get_ns
from advent23_tests.examples import get_ans, get_input


@pytest.fixture()
def ns(request) -> SimpleNamespace:
    """Puzzle namespace."""
    args = request.param
    day, user, part = args
    return get_ns(day, user, part, get_input(day, part))


@pytest.fixture()
def ans(request):
    """Puzzle answer."""
    args = request.param
    day, part = args
    return get_ans(day, part)
