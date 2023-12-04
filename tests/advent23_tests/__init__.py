"""Tests for the Advent of Code 2023."""

from collections.abc import Iterator
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal, TypeAlias

import pytest
from boilercore.hashes import hash_args
from boilercore.notebooks.namespaces import (
    NO_ATTRS,
    Attributes,
    get_nb_client,
    parametrize_notebook,
)
from cachier import cachier

from advent23_tests.answers import ANSWERS

INPUT = Path("input")
"""Input directory."""
PACKAGE = Path("src/advent23")
"""Package to test."""
ATTRIUTES = [
    f"{attr}_{part}".upper() for attr in ("ans", "checks") for part in ("a", "b")
]
"""Attributes to include in notebook namespaces for tests.

Not all notebook attributes are guaranteed pickleable, even with `dill`, and we can't
look ahead to see if it'll pickle properly, so let's just get the attributes we know
should pickle successfully.

We could compose a list of pickleable attributes by looking at `dill`'s dispatch table
and documentation.
"""


def parametrize(
    user: str, day: str, other_user: str | None = None, check: bool = False
):
    """Parametrize cases by user, day, other user, and whether to run checks."""
    return pytest.mark.parametrize(
        ("ans", "exp"),
        [
            pytest.param(*(param, param), id=param.id, marks=param.marks)
            for part in ("a", "b")
            for param in get_params(user, day, part, other_user, check)
        ],
        indirect=True,
    )


Part: TypeAlias = Literal["a", "b"]
"""Puzzle part."""

NO_MARKS = ()


@dataclass
class Case:
    """Puzzle test case."""

    user: str
    day: str
    part: Part
    other_user: str | None = None

    @property
    def id(s) -> str:  # noqa: A003
        """Get test ID."""
        return "_".join([e for e in (s.part, s.other_user) if e])

    @property
    def marks(s) -> tuple[pytest.MarkDecorator, ...]:
        """Test marks."""
        return get_marks(s.user, s.id, s.nb, s.inp, s.answer, s.expected)

    @property
    def answer(s):
        """Given answer."""
        return getattr(s.ns, f"ANS_{s.part.upper()}", None)

    @property
    def expected(s):
        """Expected answer."""
        return s.answers[s.part]["ans"]

    @property
    def answers(s) -> dict[str, Any]:
        """Expected answers for all parts, cases, and checks."""
        return ANSWERS[s.day][s.other_user or s.user]

    @property
    def ns(s) -> SimpleNamespace:
        """Notebook namespace."""
        if not s.nb or not s.inp:
            return SimpleNamespace()
        return get_cached_nb_ns(
            nb=s.nb,
            params=(
                {f"INPUT_{part}".upper(): s.inp for part in ("a", "b")} if s.inp else {}
            ),
        )

    @property
    def nb(s) -> str:
        path = PACKAGE / s.user / f"day{s.day}.ipynb"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @property
    def inp(s) -> str:
        """Test input."""
        user = s.other_user or s.user
        path = INPUT / user / f"day{s.day}.txt"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @property
    def checkpoints(s) -> dict[str, Any]:
        """Expected checkpoints."""
        return s.answers[s.part]["chk"] or {}


@dataclass
class Check:
    """Puzzle test check."""

    case: Case
    check: str

    @property
    def id(s) -> str:  # noqa: A003
        return f"{s.case.id}_{s.check}"

    @property
    def marks(s) -> tuple[pytest.MarkDecorator, ...]:
        return get_marks(s.case.user, s.id, s.case.nb, s.case.inp, s.answer, s.expected)

    @property
    def answer(s):
        """Given answer."""
        checks = getattr(s.case.ns, f"CHECKS_{s.case.part.upper()}", None)
        return checks.get(s.check) if checks else None

    @property
    def expected(s):
        """Expected answer."""
        return s.case.checkpoints.get(s.check)


def get_marks(user, id_, nb, inp, ans, exp) -> tuple[pytest.MarkDecorator, ...]:
    """Get marks based on requirements."""
    id_ = f"{user}_{id_}"
    return (
        pytest.mark.skipif(not nb, reason=f"{id_}: No notebook"),
        pytest.mark.skipif(not inp, reason=f"{id_}: No input"),
        pytest.mark.skipif(not ans, reason=f"{id_}: No attempt"),
        pytest.mark.xfail(
            not exp, reason=f"{id_}: No expected answer", raises=AssertionError
        ),
    )


def get_params(
    user: str, day: str, part: Part, other_user: str | None, check: bool
) -> Iterator[Case | Check]:
    case = Case(user, day, part, other_user)
    if check:
        yield from (Check(case, check) for check in case.checkpoints)
    else:
        yield case


Params: TypeAlias = dict[str, Any]
"""Notebook parameters."""
NO_PARAMS = {}
"""No notebook parameters."""


# TODO: Cut new release of boilercore and unpatch
def get_nb_ns_PATCHED(  # noqa: N802
    nb: str, params: Params = NO_PARAMS, attributes: Attributes = NO_ATTRS
) -> SimpleNamespace:
    """Get notebook namespace, optionally parametrizing it."""
    nb_client = get_nb_client(nb)
    if params:
        parametrize_notebook(nb_client._nb, parameters=params)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    namespace = nb_client.get_namespace()
    return SimpleNamespace(
        **(
            {attr: namespace[attr] for attr in attributes if namespace.get(attr)}
            if attributes
            else namespace
        )
    )


@cachier(hash_func=partial(hash_args, get_nb_ns_PATCHED))
def get_cached_nb_ns(nb: str, params: Params = NO_PARAMS) -> SimpleNamespace:
    """Get cached minimal namespace suitable for passing to a receiving function."""
    return get_nb_ns_PATCHED(nb, params, attributes=ATTRIUTES)
