"""Collaboration on Advent of Code 2023."""

from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from re import compile
from typing import Any, Literal

from IPython.core.display import Markdown
from IPython.display import display

HIDE = display()
"""Hide unwanted output for a notebook code cell."""


class CheckDict(UserDict[str, Any]):
    """Display items when they are set."""

    def __setitem__(self, key: Any, item: Any) -> None:
        label = make_readable(key)
        if item:
            disp_name(label, item)
        return super().__setitem__(key, item)


def get_chk():
    """Puzzle checkpoints."""
    return CheckDict()


def get_inp(day: int | str, user: str = ""):
    """Puzzle inputs, with either example or full inputs filled in `a` and `b`."""
    d = (str(day) if isinstance(day, int) else day).zfill(2)
    return CheckDict(
        {p: get_full_inp(d, user) if user else get_ex_inp(d, p) for p in ("a", "b")}
    )


INPUT = Path("input")


def get_ex_inp(day: str, part: Literal["a", "b"]) -> str:
    """Get example inputs for a puzzle day and part."""
    path = INPUT / f"ex_{part}" / f"{day}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def get_full_inp(day: str, user: str) -> str:
    """Get full inputs for a puzzle day and user."""
    path = INPUT / user / f"{day}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


@dataclass
class Checker:
    chk: CheckDict

    def __call__(self, name: str, ans):
        assert ans == self.chk[name]  # noqa: S101

    def disp(self, name: str, ans):
        disp_name(name, self.chk[name])
        self.__call__(name, ans)


def disp_names(*args: tuple[str, Any]):
    """Display objects with names above them."""
    for name, elem in args:
        disp_name(name, elem)


def disp_name(name: str, elem: Any):
    """Display an object with its name above it."""
    display(Markdown(f"#### {make_readable(name)}"))
    print(truncate(elem)) if isinstance(elem, str) else display(elem)  # noqa: T201


def make_readable(string: str) -> str:
    """Get a human-readable string."""
    s = string
    for suf in (suf for suf in ("a", "b") if s.endswith(f"_{suf}")):
        s = f"{s.removesuffix(f'_{suf}')} {suf.upper()}"
    s = f"Answer {s.removeprefix('ans')}" if s.startswith("ans") else s
    s = f"{s.replace('_', ' ')}"
    return f"{s[0].upper()}{s[1:]}"


LONG_STRING = compile(r"(?P<first>(?:.*\n){10}).*")
"""A long string."""


def truncate(string: str) -> str:
    """Truncate long strings."""
    return LONG_STRING.sub(r"\g<first>... <long result truncated> ...\n", string)
