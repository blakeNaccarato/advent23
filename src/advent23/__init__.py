"""Collaboration on Advent of Code 2023."""

from collections import UserDict
from typing import Any

from IPython.core.display import Markdown
from IPython.display import display


class CheckDict(UserDict[str, Any]):
    """Dictionary that displays the key and value when set."""

    def __setitem__(self, key: Any, item: Any) -> None:
        disp_name(f"{key.capitalize().replace('_', ' ')}:", item)
        return super().__setitem__(key, item)


CHECKS_A = CheckDict()
CHECKS_B = CheckDict()


def disp_names(*args: tuple[str, Any]):
    """Display objects with names above them."""
    for name, elem in args:
        disp_name(name, elem)


def disp_name(name: str, elem: Any):
    """Display an object with its name above it."""
    display(Markdown(f"#### {name}"))
    display(elem)
