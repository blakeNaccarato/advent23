"""Blake's solutions."""

from collections.abc import Iterator, MutableMapping
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from typing import Self

from more_itertools import last


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, *, root: str, **patterns: Self | str) -> None:
        self.root = root
        self.patterns = patterns
        super().__init__()

    def sub(self, **other_patterns: Self | str) -> str:
        return (last(self.subber(**other_patterns), default=self.root)).replace(
            "$$", "$"
        )

    def subber(self, **other_patterns: Self | str) -> Iterator[str]:
        result = self.root
        while result != (
            result := Template(result.replace("$$", "$$$$")).substitute(
                {
                    name: pattern if isinstance(pattern, str) else pattern.subber()
                    for name, pattern in {**self.patterns, **other_patterns}.items()
                }
            )
        ):
            yield result

    def __getitem__(self, key: str) -> Self | str:  # type: ignore
        return self.patterns[key]

    def __setitem__(self, key: str, pattern: Self | str):
        self.patterns[key] = pattern

    def __delitem__(self, key: str):
        del self.patterns[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.patterns)

    def __len__(self) -> int:
        return len(self.patterns)


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)
