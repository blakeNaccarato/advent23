"""Test configuration."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from boilercore.notebooks.namespaces import get_nb_ns

from advent23_tests import Args, get_ans


@pytest.fixture()
def ns(request) -> SimpleNamespace:
    """Notebook namespace."""
    args: Args = request.param
    user, day, basic = args
    params = (
        {"INPUT": Path(f"input_basic/day{day}.txt").read_text(encoding="utf-8")}
        if basic
        else {"INPUT": request.getfixturevalue(f"day{day}_raw")}
    )
    return get_nb_ns(
        nb=Path(f"src/advent23/{user}/day{day}.ipynb").read_text(encoding="utf-8"),
        params=params,
    )


@pytest.fixture()
def ans(request):
    """Answer."""
    args: Args = request.param
    _user, day, basic = args
    return get_ans(day, basic)
