"""Tests for the Advent of Code 2023."""

from ast import Assign, Constant, Name, NodeVisitor, Subscript, parse, walk
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Self

import pytest
from _pytest.mark.structures import ParameterSet
from nbformat import NO_CONVERT, NotebookNode, reads

from advent23_tests.answers import CHECKS
from advent23_tests.namespaces import get_cached_nb_ns

OTHER = "blake"
"""Other user for comparisons."""
PACKAGE = Path("src/advent23")
"""Package to test."""
INPUT = Path("input")
"""Input directory."""
PARTS = ("a", "b")
"""Parts of the puzzle."""
EXAMPLES = {f"ex_{part}": f"ans_{part}" for part in PARTS}
"""Example inputs."""


def parametrize(user: str, day: str):
    """Parametrize cases by user and day."""
    attempt = Attempt(user, day)
    return get_params(
        pytest.param(
            *([Case(attempt, check)] * 2),
            id=attempt.id(check),
            marks=attempt.marks(check),
        )
        for check in attempt.checks
        if check in EXAMPLES.values()
    )


def parametrize_other(user: str, day: str, other_user: str):
    """Parametrize cases by user, day, and other user."""
    attempt = Attempt(user, day)
    other = Attempt(other_user, day)
    checks = {
        c: str(i).zfill(2)
        for i, c in enumerate([c for c in attempt.checks if c in other.checks])
    }
    return get_params(
        pytest.param(
            *([Case(attempt, check, other)] * 2),
            id=attempt.id(check, i),
            marks=attempt.marks(check, other),
        )
        for check, i in checks.items()
    )


def parametrize_ex(user: str, day: str):
    """Parametrize cases by user and day for example inputs."""
    attempt = Attempt(user, day)
    return get_params(
        pytest.param(
            *([Case(attempt, check, ex)] * 2),
            id=attempt.id(check),
            marks=attempt.marks(check, ex),
        )
        for check, ex in {
            check: Attempt(ex, day) for ex, check in EXAMPLES.items()
        }.items()
        if ex.expected(check)
    )


def get_params(params: Iterator[ParameterSet]):
    return pytest.mark.parametrize(("ans", "exp"), list(params), indirect=True)


def get_ex_inp(day: str):
    return {
        part: Attempt(ex, day).inp() for part, ex in zip(PARTS, EXAMPLES, strict=True)
    }


@dataclass
class Attempt:
    """A puzzle attempt."""

    user: str
    """The user attempting the puzzle."""
    day: str
    """The day of the puzzle."""

    @property
    def nb(self) -> str:
        path = PACKAGE / self.user / f"day{self.day}.ipynb"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    @property
    def checks(self):
        """Attempted checks."""
        src = "\n".join(
            c.source.strip()
            for c in reads(self.nb, NO_CONVERT).cells  # type: ignore  # pyright: 1.1.377
            if c.cell_type == "code"
        )
        visitor = ChkVisitor()
        visitor.visit(parse(src))
        return visitor.checks

    def answer(self, check: str, other: Self | None = None):
        """Given answer."""
        if other:
            params = {"inp": get_ex_inp(self.day)}
        else:
            inp = self.inp()
            params = {"inp": {part: inp for part in PARTS}}
        ns = get_cached_nb_ns(nb=self.nb, params=params)
        chk = getattr(ns, "chk", None)
        return chk.get(check) if chk else None

    def expected(self, check: str, other: Self | None = None):
        """Expected answer."""
        if other and other.user in EXAMPLES:
            return other.expected(check)
        if other:
            return other.answer(check, other)
        if not other and self.user in EXAMPLES:
            return CHECKS[self.day].get(self.user)
        return CHECKS[self.day][self.user].get(check)  # type: ignore

    def inp(self) -> str:
        """Test input."""
        if (path := INPUT / self.user / f"{self.day}.txt").exists():
            return path.read_text(encoding="utf-8")
        return ""

    def id(self, check: str, pos: str = "") -> str:  # noqa: A003
        """Test ID."""
        return "_".join([e for e in (pos, check) if e])

    def marks(
        self, check: str, other: Self | None = None
    ) -> tuple[pytest.MarkDecorator, ...]:
        """Test marks."""
        return (
            *(
                pytest.mark.skipif(bool(cond), reason=f"{self.id}: {reason}")
                for reason, cond in {
                    "No notebook": not self.nb,
                    "No input": not self.inp() or (other and not other.inp()),
                }.items()
            ),
            *(
                pytest.mark.xfail(
                    bool(cond),
                    reason=f"{self.id(check)}: {reason}",
                    raises=AssertionError,
                )
                for reason, cond in {
                    "Not answered": not other and not self.expected(check)
                }.items()
            ),
        )


class Case(NamedTuple):
    """Test case."""

    attempt: Attempt
    check: str
    other: Attempt | None = None


def get_checks(nb: NotebookNode) -> list[str]:
    """Get valid checks."""
    src = "\n".join(c.source.strip() for c in nb.cells if c.cell_type == "code")
    visitor = ChkVisitor()
    visitor.visit(parse(src))
    return visitor.checks


class ChkVisitor(NodeVisitor):
    def __init__(self):
        """Visitor that finds non-constant checks."""
        self.names: list[str] = []
        self.checks: list[str] = []

    def visit_Assign(self, node: Assign):  # noqa: N802
        """Visit variable assignments, looking for checks.

        Valid checks look like the following:

        ```Python
        chk["literal_string_key"] = ...
        ```
        """
        # Find variable names on the LHS of assignments
        if isinstance((target := node.targets[0]), Name):
            self.names.append(target.id)
        # Validate checks
        if (
            # Indexing appears on the LHS, e.g. `name[...]`
            isinstance((target := node.targets[0]), Subscript)
            # The variable on the LHS is the `chk` variable, e.g. `chk[...]`
            and isinstance((name := target.value), Name)
            and name.id == "chk"
            # The indexer is a name not a slice, e.g. `chk[named_index]`, not `0:10:2`
            and isinstance((index := target.slice), Constant)
            # The RHS references one of the variable names previously encountered
            and any(
                n.id
                for n in walk(node.value)
                if isinstance(n, Name) and n.id in self.names
            )
        ):
            # The check is valid e.g. `valid_check` in `chk["valid_check"] = ...`
            self.checks.append(index.value)
        self.generic_visit(node)
