"""Test attempts."""

from __future__ import annotations

from ast import Assign, Constant, Name, NodeVisitor, Subscript, parse, walk
from collections.abc import Callable, Hashable, Iterator
from dataclasses import dataclass
from functools import partial
from inspect import getsource, signature
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Self, TypeAlias

from boilercore.notebooks.namespaces import (
    NO_ATTRS,
    NO_PARAMS,
    Attributes,
    get_nb_client,
    parametrize_notebook,
)
from cachier import cachier
from cachier.core import _default_hash_func  # type: ignore
from nbformat import NO_CONVERT, reads

from advent23 import EXAMPLES

ATTEMPTS = Path("src/advent23")
"""Location of attempts."""
USERS = ("blake", "abdul", "brad")
"""Users to test."""


def walk_attempts(other_user: str = "") -> Iterator[Attempt]:
    """Walk the attempts for all users, optionally comparing against another user.

    Args:
        other_user: Optionally, another user's attempts to compare against.
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
        """Get the user's answer for a checkpoint in this attempt.

        The notebook should have `chk` and `inp` mappings.

        Args:
            check: Checkpoint name.
        """
        ns = get_cached_notebook_namespace_PATCHED(
            nb=self.nb, params={"inp": self.inp}, attributes=["chk", "inp"]
        )
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

    def get_id(self, check: str, pos: int | None = None) -> str:
        """Get the test ID associated with this attempt.

        Args:
            check: Checkpoint name.
            pos: Optionally, position of this checkpoint in the test group.
        """
        return "_".join(
            [p for p in (self.user, f"day{self.day}", str(pos).zfill(2), check) if p]
        )


def get_attempted_checks(src: str) -> list[str]:
    """Get attempted checkpoints from source code."""
    visitor = ChkVisitor()
    visitor.visit(parse(src))
    return visitor.checks


class ChkVisitor(NodeVisitor):
    def __init__(self):
        """Visit variable assignments, looking for valid checkpoints.

        Valid checkpoints are assignments to a key in the `chk` mapping which reference a
        previous variable. Valid checks look like the following:

        ```Python
        chk["literal_string_key"] = <variable referenced somewhere here>
        ```

        Attributes:
            names: Names of variables encountered in the notebook.
            checks: Checkpoints attempted in the notebook.
        """
        self.names: set[str] = set()
        self.checks: list[str] = []

    def visit_Assign(self, node: Assign):  # noqa: N802
        # Find variables, e.g. names on the LHS of assignments
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
            # The RHS references an existing variable
            and any(
                n.id
                for n in walk(node.value)
                if isinstance(n, Name) and n.id in self.names
            )
        ):
            # The check is valid e.g. `valid_check` in `chk["valid_check"] = expr`
            # Where `expr` references an existing variable
            self.checks.append(index.value)
        self.generic_visit(node)


Params: TypeAlias = dict[str, Any]
"""Notebook parameters."""


def get_notebook_namespace_PATCHED(  # noqa: N802
    nb: str, params: Params = NO_PARAMS, attributes: Attributes = NO_ATTRS
) -> SimpleNamespace:
    """Get notebook namespace, optionally parametrizing or limiting returned attributes.

    Args:
        nb: Notebook contents as text.
        params: Parameters to inject below the first `parameters`-tagged code cell.
        attributes: If given, limit the notebook attributes to return in the namespace.

    Returns:
        Notebook namespace.

    Example:
        ```Python
        ns = get_notebook_namespace_PATCHED(
            nb=Path("notebook.ipynb").read_text(encoding="utf-8"),
            params={"some_parameter": 3, "other_parameter": [0, 1]},
            attributes=["results", "other_attribute_to_return"],
        )
        ```
    """
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


def hash_args_PATCHED(  # noqa: N802
    fun: Callable[..., Any], args: tuple[Any, ...], kwds: dict[str, Any]
) -> str:
    """Hash a particular set of arguments meant to be passed to a particular function.

    Passing this function, with `fun` applied via `partial`, to `cachier`'s `hash_func`
    decorator allows us to create a cacheable form of `fun`.

    Returns: Hash of the arguments.

    Args:
        fun: Function from which the signature will be generated.
        args: Positional arguments to hash.
        kwds: Keyword arguments to hash.

    Example:
        ```Python
        import cachier
        from functools import partial

        @cachier(hash_func=partial(hash_args_PATCHED, uncached_function))
        def cached_function(*args, *kwds):
            return uncached_function(*args, *kwds)
        ```
    """
    bound_args = signature(fun).bind(*args, **kwds).arguments
    return _default_hash_func(
        (), {param: make_hashable_PATCHED(val) for param, val in bound_args.items()}
    )


def make_hashable_PATCHED(value: Any) -> Hashable:  # noqa: N802
    """Make value hashable."""
    if isinstance(value, Hashable):
        return value
    for typ, transform in {
        Callable: lambda v: getsource(v),
        dict: lambda v: frozenset(
            {
                k: frozenset(v_.items()) if isinstance(v_, dict) else v
                for k, v_ in v.items()
            }.items()
        ),
        list: lambda v: frozenset(v),
    }.items():
        if isinstance(value, typ):
            return transform(value)
    raise TypeError(
        f"Value of type {type(value)} not hashable and transform not implemented."
    )


@cachier(hash_func=partial(hash_args_PATCHED, get_notebook_namespace_PATCHED))
def get_cached_notebook_namespace_PATCHED(  # noqa: N802
    nb: str, params: Params = NO_PARAMS, attributes=NO_ATTRS
) -> SimpleNamespace:
    """Get cached notebook namespace, optionally parametrizing or limiting attributes.

    This caches the return values and avoids execution if the hash of input argument
    values matches an earlier call.

    Args:
        nb: Notebook contents as text.
        params: Parameters to inject below the first `parameters`-tagged code cell.
        attributes: If given, limit the notebook attributes to return in the namespace.

    Returns:
        Notebook namespace.

    Example:
        ```Python
        ns = get_cached_notebook_namespace_PATCHED(
            nb=Path("notebook.ipynb").read_text(encoding="utf-8"),
            params={"some_parameter": 3, "other_parameter": [0, 1]},
            attributes=["results", "other_attribute_to_return"],
        )
        ```
    """
    return get_notebook_namespace_PATCHED(nb, params, attributes)
