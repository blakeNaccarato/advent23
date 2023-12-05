"""Collaboration on Advent of Code 2023."""

from collections import UserDict
from pathlib import Path
from typing import Any, Literal

from IPython.core.display import Markdown
from IPython.display import display


class CheckDict(UserDict[str, Any]):
    """Dictionary that displays the key and value when set."""

    def __setitem__(self, key: Any, item: Any) -> None:
        prefix = "ans_"
        label = (
            f"Answer {key.removeprefix(prefix).capitalize()}"
            if key.startswith(prefix)
            else f"{key.capitalize().replace('_', ' ')}"
        )
        if item:
            disp_name(label, item)
        return super().__setitem__(key, item)


def get_chk():
    """Get CheckDict for testing puzzle answers."""
    return CheckDict()


def get_inp(day: int):
    """Get CheckDict with `a` and `b` keys filled with example inputs."""
    return CheckDict(
        {part: get_example_input(str(day).zfill(2), part) for part in ("a", "b")}
    )


def get_example_input(day: str, part: Literal["a", "b"]) -> str:
    """Get example inputs for a puzzle day and part."""
    path = Path("input") / f"ex_{part}" / f"{day}.txt"
    return path.read_text(encoding="utf-8") if path.exists() else ""


HIDE = display()


def disp_check(name, result, checks):
    disp_name(name, result)
    assert result == checks[name]  # noqa: S101


def disp_names(*args: tuple[str, Any]):
    """Display objects with names above them."""
    for name, elem in args:
        disp_name(name, elem)


def disp_name(name: str, elem: Any):
    """Display an object with its name above it."""
    display(Markdown(f"#### {name}"))
    print(elem) if isinstance(elem, str) else display(elem)  # noqa: T201
