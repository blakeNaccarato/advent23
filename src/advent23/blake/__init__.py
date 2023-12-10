"""Blake's solutions."""

from collections.abc import Iterator, MutableMapping
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from typing import Self


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, *, root: str, **patterns: Self | str) -> None:
        self.root = root
        self.patterns = patterns
        super().__init__()

    def sub(self) -> str:
        return self.subber(self.get_result(self.root)).replace("$$", "$")

    def subber(self, foo: str) -> str:
        while foo != (foo := self.get_result(self.root)):
            pass
        return foo

    def get_result(self, pattern: str | Self) -> str:
        return Template(pattern.replace("$$", "$$$$")).substitute(  # type: ignore
            {
                name: pat if isinstance(pat, str) else self.get_result(pat)
                for name, pat in self.patterns.items()
            }
        )

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
