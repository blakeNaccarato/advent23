"""Tests."""

from collections.abc import Iterable
from pathlib import Path

import pytest

from advent23_tests import Args, get_ans

PACKAGE = Path("src/advent23")
"""The package to test."""


def params(basic: bool = False) -> Iterable[Args]:
    yield from (
        Args(user.name, day.stem.removeprefix("day"), basic=basic)
        for user in [PACKAGE / "_template", *PACKAGE.glob("[!_]*")]
        for day in Path("input").iterdir()
    )


BASIC = params(basic=True)
"""Parameters given in the prompt."""

FULL = params()
"""Parameters found by solving the problem."""


def _parametrize(*params: Args):
    """Local test parametrization shorthand."""
    return pytest.mark.parametrize(
        ("ns", "ans"),
        [
            pytest.param(
                p,
                p,
                id=f"{p.user}_{p.day}",
                marks=(
                    pytest.mark.skip
                    if not p.basic
                    and (p.user == "_template" or get_ans(p.day, p.basic) is None)
                    else []
                ),
            )
            for p in params
        ],
        indirect=["ns", "ans"],
    )


@_parametrize(*BASIC)
def test_basic(ns, ans):
    """Test for day 1."""
    assert ns.OUTPUT == ans


@_parametrize(*FULL)
def test_full(ns, ans):
    """Test for day 1."""
    assert ns.OUTPUT == ans
