"""Collaboration on Advent of Code 2023."""

from __future__ import annotations

from collections import UserDict
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from re import compile
from tomllib import loads
from typing import Any
from warnings import warn

from IPython.core.display import Markdown
from IPython.display import display

LIMIT = 15
"""Line limit before output will be truncated."""
PARTS = ("a", "b")
"""Parts of the puzzle."""
INPUT = Path("input")
"""Location of inputs for attempts."""
HIDE = display()
"""Hide unwanted output for a notebook code cell."""


@dataclass
class Example:
    """Puzzle example."""

    inp: dict[str, str]
    """Inputs for each part."""
    chk: dict[str, Any]
    """Checkpoint dictionary."""


EXAMPLES = {
    str(ex["day"]).zfill(2): Example(ex["inp"], ex["chk"])
    for ex in loads((INPUT / "examples.toml").read_text(encoding="utf-8"))["example"]
}


def get_chk():
    """Puzzle checkpoints."""
    return CheckDict()


def get_inp(day: int | str, user: str = "", part: str = "") -> CheckDict:
    """Puzzle inputs, with either example or full inputs filled in `a` and `b`."""
    d = str(day).zfill(2) if isinstance(day, int) else day
    example_inputs = EXAMPLES[d].inp
    if not user:
        return CheckDict(example_inputs)
    full_input = (INPUT / user / f"{d}.txt").read_text(encoding="utf-8")
    return CheckDict(
        example_inputs
        | ({part: full_input} if part else {part: full_input for part in PARTS})
    )


@dataclass
class Checker:
    chk: CheckDict

    def __call__(self, name: str, ans):
        try:
            expected = self.chk[name]
        except KeyError as err:
            raise KeyError(f'Checkpoint "{name}" not found.') from err
        try:
            assert ans == expected  # noqa: S101
        except AssertionError:
            display(Markdown(f'### "{make_readable(name)}" check failed'))
            disp_name("Expected", self.chk[name])
            disp_name("Your answer", ans)
            raise


class CheckDict(UserDict[str, Any]):
    """Display items when they are set."""

    def __setitem__(self, key: Any, item):
        if item is None:
            warn(f'Set  "{key}" to `None`.', stacklevel=2)
        if item == "":
            warn(f'Set  "{key}" to `""` (empty string).', stacklevel=2)
        disp_name(make_readable(key), item)
        return super().__setitem__(key, item)


def disp_names(*args: tuple[str, Any]):
    """Display objects with names above them."""
    for name, elem in args:
        disp_name(name, elem)


def disp_name(name: str, elem: Any):
    """Display an object with its name above it."""
    display(Markdown(f"#### {make_readable(name)}"))
    if isinstance(elem, str):
        print(truncate(str(elem)))  # noqa: T201
        return
    if isinstance(elem, Collection) and len(elem) > LIMIT:
        print(truncate(str(elem).replace(",", ",\n")))  # noqa: T201
        return
    display(elem)


def truncate(string: str) -> str:
    """Truncate long strings."""
    if match := long_string.match(string):
        return f"{match.group()}\n... <long result truncated> ..."
    return string


long_string = compile(rf"^(?P<first>(?:.*\n){{{LIMIT}}}).*")
"""String with lots of newlines."""


def make_readable(string: str) -> str:
    """Get a human-readable string."""
    s = string
    if s in {"a", "b"}:
        s = f"part {1 if s == 'a' else 2}"
    s = f"{s.replace('_', ' ')}"
    return f"{s[0].upper()}{s[1:]}"
