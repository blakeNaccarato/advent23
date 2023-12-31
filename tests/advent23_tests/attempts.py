"""Test attempts."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from re import MULTILINE, compile
from typing import Self

from astroid import Assign, AssignName, Const, List, Uninferable, extract_node
from astroid.exceptions import InferenceError
from boilercore.notebooks.namespaces import get_nb_ns
from nbformat import NO_CONVERT, reads

from advent23 import EXAMPLES

ATTEMPTS = Path("src/advent23")
"""Location of attempts."""
USERS = ("blake", "abdul", "brad", "together")
"""Users to test."""


def walk_attempts(other_user: str = "") -> Iterator[Attempt]:
    """Walk all user attempts, optionally comparing against another user.

    Yields:
        Attempts of all users, optionally comparing against another user.

    Args:
        other_user (optional): Another user's attempts to compare against.
    """
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
        """Attempted checkpoints retrieved from the notebook's `chk` mapping.

        Uses a heuristic that finds intentionally attempted checkpoints, rather than
        those that trivially obtain the correct answer to a hard-coded example, as in
        the initial template notebook that most users start from.

        Finds keys of `chk` associated with assignments in which the right-hand-side of
        the assignment references an earlier variable.
        """
        return [
            check
            for check in get_attempted_checks(self.nb)
            if check in (self.other.checks if self.other else EXAMPLES[self.day].chk)
        ]

    @property
    def nb(self) -> str:
        """Jupyter notebook associated with this user's attempt."""
        path = ATTEMPTS / self.user / f"day{self.day}.ipynb"
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def get_answer(self, check: str):
        """Get the user's answer for a checkpoint in this attempt.

        The notebook should have `chk` and `inp` mappings.

        Args:
            check: Checkpoint name.
        """
        ns = get_nb_ns(nb=self.nb, params={"inp": self.inp}, attributes=["chk", "inp"])
        return chk.get(check) if (chk := getattr(ns, "chk", None)) else None

    def get_expected_answer(self, check: str):
        """Get the expected answer for a checkpoint.

        If `other` was specified when setting up this attempt, the expected answer is
        the value of the check from running that user's attempt. Otherwise, get the
        result of the check from the example input.

        Args:
            check: Checkpoint name.
        """
        return (
            self.other.get_answer(check)
            if self.other
            else EXAMPLES[self.day].chk.get(check)
        )

    def get_id(self, check: str) -> str:
        """Get the test ID associated with this attempt.

        Args:
            check: Checkpoint name.
            pos: Optionally, position of this checkpoint in the test group.
        """
        return "_".join([p for p in (self.user, f"day{self.day}", check) if p])


CHECKS = compile(pattern=r'(?P<line>^chk\["(?P<check>[\w_]+)"\].+$)', flags=MULTILINE)
"""Find notebook-level assignments to a `chk` mapping.

Group matches by line and checkpoint name.
"""

CHECK_ALSO = compile(pattern=r"(?P<line>^CHECK_ALSO.+$)", flags=MULTILINE)
"""Find notebook-level assignments to `CHECK_ALSO`.

Group matches by line.
"""

CHECKS_REPL = r"\g<line>  #@"
"""Annotate checks for node extraction with `astroid`."""


def get_attempted_checks(nb: str) -> list[str]:
    """Get names of attempted checkpoints from notebook contents.

    Use `astroid` to infer possible values of assignments to `chk["..."]`. If inference
    fails, or an uninferable value is found, assume the checkpoint was attempted. This
    tends to identify non-trivial right-hand-sides, excluding checks assigned to
    hardcoded constants as in starter template notebooks.

    Also add checks assigned as `CHECK_ALSO`.

    Returns:
        List of attempted checkpoints.

    Args:
        nb: Jupyter notebook contents.
    """
    src = "\n".join(
        c.source.strip()
        for c in reads(nb, NO_CONVERT).cells  # type: ignore  # pyright: 1.1.377
        if c.cell_type == "code"
    )
    # Finc `chk` mapping assignments and `CHECK_ALSO` overrides
    checks = (match["check"] for match in CHECKS.finditer(src))
    # Append `#@` annotations to tell `astroid` which nodes to extract
    for pattern in (CHECKS, CHECK_ALSO):
        src = pattern.sub(repl=CHECKS_REPL, string=src)
    # `extract_node` unpacks singletons, so wrap in list for consistency
    nodes = nodes if isinstance((nodes := extract_node(src)), list) else [nodes]
    attempted_checks: list[str] = []
    for node in nodes:
        # Extracted nodes should all be assignments, but guard against it anwyays
        if not isinstance(node, Assign):
            continue
        # Handle `CHECK_ALSO` assignments
        if (
            isinstance(target := (node.targets[0]), AssignName)
            and target.name == "CHECK_ALSO"
        ):
            rhs = node.value
            if isinstance(rhs := node.value, List):
                attempted_checks.extend([
                    elt.value for elt in rhs.elts if isinstance(elt, Const)
                ])
            elif isinstance(rhs, Const):
                attempted_checks.append(rhs.value)
            continue
        # Handle `chk` assignments
        check = next(checks)
        # The check is likely an organic attempt if inference fails...
        try:
            inferences = list(node.value.infer())
        except InferenceError:
            attempted_checks.append(check)
            continue
        # ...or if any returned value is considered uniferable
        if any(inf is Uninferable for inf in inferences):
            attempted_checks.append(check)
            continue
        # ...or if any composite value (e.g. a dict) is considered uniferable
        if any(inf.bool_value() is Uninferable for inf in inferences):
            attempted_checks.append(check)
    return attempted_checks
