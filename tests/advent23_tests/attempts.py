"""Test attempts."""

from __future__ import annotations

from ast import Assign, Constant, Name, NodeVisitor, Subscript, parse, walk
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from nbformat import NO_CONVERT, reads

from advent23 import EXAMPLES
from advent23_tests.namespaces import get_cached_nb_ns

ATTEMPTS = Path("src/advent23")
"""Location of attempts."""
USERS = ("blake", "abdul", "brad")
"""Users to test."""


def get_attempts(other_user: str = "") -> Iterator[Attempt]:
    for day in EXAMPLES:
        other = Attempt(other_user, day) if other_user else None
        yield from (
            att
            for att in (Attempt(user, day, other) for user in USERS)
            if att.nb and att.inp
            if other_user and att.user != other_user or not other_user
        )


@dataclass
class Attempt:
    """Puzzle attempt."""

    user: str
    """User attempting the puzzle."""
    day: str
    """Zero-padded puzzle day."""
    other: Self | None = None
    """Another user's attempt to compare against."""

    @property
    def inp(self) -> dict[str, str]:
        """Example input for this attempt."""
        return EXAMPLES[self.day].inp

    @property
    def checks(self) -> list[str]:
        """Attempted checkpoints retrieved from the notebook's `chk` dictionary.

        Represents assignments to the `chk` dictionary in the user's notebook in which
        the right-hand-side of the assignment references at least one other variable in
        their notebook. This heuristic identifies checks which are likely to be
        intentionally attempted, rather than those hard-coded to a correct answer as in
        the initial template notebook that most users start from.
        """
        checks = get_attempted_checks(
            "\n".join(
                c.source.strip()
                for c in reads(self.nb, NO_CONVERT).cells  # type: ignore  # pyright: 1.1.377
                if c.cell_type == "code"
            )
        )
        if self.other:
            return [c for c in checks if c in self.other.checks]
        return [c for c in checks if c in EXAMPLES[self.day].chk]

    @property
    def nb(self) -> str:
        """Jupyter notebook associated with this user's attempt."""
        path = ATTEMPTS / self.user / f"day{self.day}.ipynb"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def get_answer(self, check: str):
        """The user's answer for a checkpoint in this attempt."""
        ns = get_cached_nb_ns(nb=self.nb, params={"inp": self.inp})
        return chk.get(check) if (chk := getattr(ns, "chk", None)) else None

    def get_expected_answer(self, check: str):
        """Get the expected answer for a checkpoint.

        If `other` was specified when setting up this attempt, the expected answer is
        the value of the check from running that user's attempt. Otherwise, get the
        result of the check from the example input.
        """
        return (
            self.other.get_answer(check)
            if self.other
            else EXAMPLES[self.day].chk.get(check)
        )

    def get_id(self, check: str, pos: str = "") -> str:
        """Test ID."""
        return "_".join([p for p in (self.user, f"day{self.day}", pos, check) if p])


def get_attempted_checks(src: str) -> list[str]:
    visitor = ChkVisitor()
    visitor.visit(parse(src))
    return visitor.checks


class ChkVisitor(NodeVisitor):
    def __init__(self):
        """Visitor that finds attempted checks."""
        self.names: set[str] = set()
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
            self.names.add(target.id)
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
