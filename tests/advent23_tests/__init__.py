"""Tests for the Advent of Code 2023."""

from pathlib import Path
from types import SimpleNamespace
from typing import Literal, TypeAlias

from boilercore.notebooks.namespaces import get_nb_ns

Part: TypeAlias = Literal["a", "b"]
"""Puzzle part."""

INPUT = Path("input")
"""Input directory."""
PACKAGE = Path("src/advent23")
"""Package to test."""


def get_nb(day: str, user: str, part: Part):
    """Get notebook contents."""
    return (
        (PACKAGE / user / f"day{day}{part}")
        .with_suffix(".ipynb")
        .read_text(encoding="utf-8")
    )


def get_ns(day: str, user: str, part: Part, inp: str) -> SimpleNamespace:
    """Puzzle namespace."""
    return get_nb_ns(nb=get_nb(day, user, part), params={"INPUT": inp})
