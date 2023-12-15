"""Collaboration on Advent of Code 2023."""

from __future__ import annotations

from collections import UserDict
from collections.abc import Callable, Collection, MutableMapping
from dataclasses import dataclass
from pathlib import Path
from re import MULTILINE, Pattern, compile
from tomllib import loads
from typing import Any, TypeAlias
from warnings import warn

from IPython.core.display import Markdown
from IPython.display import display

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

    def __post_init__(self):
        if not self.inp.get("b"):
            self.inp["b"] = self.inp["a"]


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


PatternCheck: TypeAlias = Callable[[Pattern[str]], Any]
PatternChecks: TypeAlias = MutableMapping[str, PatternCheck]

NO_CHECKS = {}


class CheckDict(UserDict[str, Any]):
    """Display items when they are set."""

    def __setitem__(self, key, item):
        super().__setitem__(key, item)
        if item is None:
            warn(f'Set  "{key}" to `None`.', stacklevel=2)
        if item == "":
            warn(f'Set  "{key}" to `""` (empty string).', stacklevel=2)
        if key == "b" and (a := self.get("a")) and item == a:
            item = "<same as part 1>"
        disp_name(make_readable(key), item)


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
    if isinstance(elem, Collection) and len(elem) > LINE_LIMIT:
        print(truncate(str(elem).replace(",", ",\n")))  # noqa: T201
        return
    display(elem)


def truncate(string: str) -> str:
    """Truncate long strings."""
    string = (
        f"{match.group()}... <view truncated> ..."
        if (match := long_string.match(string))
        else string
    )
    if any(wide_strings(string)):
        lines = truncated_lines(string)
        lines[0] = f"{lines[0]}{WIDTH_MSG_FIRST}"
        string = lines[0] + "\n" + f"{WIDTH_MSG}\n".join(lines[1:])
    return string


LINE_LIMIT = 15
"""Line limit before output will be truncated."""
long_string = compile(rf"^(?:.*\n){{{LINE_LIMIT}}}")
"""String with lots of newlines."""
WIDTH_MSG_FIRST = " <...view truncated>"
WIDTH_MSG = " <...>"
WIDTH_LIMIT = 88 - len(WIDTH_MSG_FIRST)
"""Width limit before lines will be truncated."""
wide_strings = compile(rf"^.{{{WIDTH_LIMIT},}}", flags=MULTILINE).findall
"""List of long lines."""
truncated_lines = compile(rf"^.{{,{WIDTH_LIMIT}}}", flags=MULTILINE).findall
"""List of all lines, truncated to maximum width."""


def make_readable(string: str) -> str:
    """Get a human-readable string."""
    s = string
    if s in {"a", "b"}:
        s = f"part {1 if s == 'a' else 2}"
    s = f"{s.replace('_', ' ')}"
    return f"{s[0].upper()}{s[1:]}"
