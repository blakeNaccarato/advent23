"""Test configuration."""

from types import SimpleNamespace

import pytest

from advent23_tests import Case


@pytest.fixture()
def ns(request) -> SimpleNamespace:
    """Puzzle namespace."""
    case: Case = request.param
    return case.ns


@pytest.fixture()
def expected(request):
    """Puzzle answer."""
    case: Case = request.param
    return case.expected
