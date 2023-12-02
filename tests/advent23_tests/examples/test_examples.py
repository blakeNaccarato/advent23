"""Tests for examples given in the prompts."""

import pytest

from advent23_tests.answers import ANSWERS
from advent23_tests.examples import get_ans

params = [
    (day, user, part)
    for user in ANSWERS["01"]
    for day in ANSWERS
    for part in ("a", "b")
]


@pytest.mark.parametrize(
    ("ns", "ans"),
    [
        pytest.param(
            p,
            (p[0], p[2]),
            id="".join([p[1], p[0], p[2]]),
            marks=(pytest.mark.skip if get_ans(p[0], p[2]) is None else []),
        )
        for p in params
    ],
    indirect=["ns", "ans"],
)
def test_puzzles(ns, ans):
    """Tests for examples given in the prompts."""
    assert ns.OUTPUT == ans
