"""Collaboration on Advent of Code 2023."""

from typing import Any

from IPython.core.display import Markdown
from IPython.display import display


def disp_names(*args: tuple[str, Any]):
    """Display objects with names above them."""
    for name, elem in args:
        disp_name(name, elem)


def disp_name(name: str, elem: Any):
    """Display an object with its name above it."""
    display(Markdown(f"#### {name}"))
    display(elem)
