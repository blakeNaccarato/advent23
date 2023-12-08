"""Tests for the Advent of Code 2023."""

from pathlib import Path

ATTEMPTS = Path("src/advent23")
"""Location of attempts."""
INPUT = Path("input")
"""Location of inputs for attempts."""

USERS = ("blake", "abdul", "brad")
"""Users to test."""
OTHER = "blake"
"""Other user for comparisons."""

DAYS = [str(i).zfill(2) for i in range(1, 26)]
"""Days in the Advent."""
PARTS = ("a", "b")
"""Parts of the puzzle."""
EXAMPLES = {f"ex_{part}": f"ans_{part}" for part in PARTS}
"""Example inputs and their associated answers."""
