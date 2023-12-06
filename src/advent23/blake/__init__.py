"""Blake's solutions."""

from collections.abc import Iterator, MutableMapping
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from types import SimpleNamespace

from more_itertools import last


class Stringer(MutableMapping[str, str]):
    def __init__(self, root: str, **patterns: str) -> None:
        self._templates: dict[str, str] = {"root": root} | patterns
        self._root = root
        self.ns = SimpleNamespace(**self._templates)
        super().__init__()

    def sub(self, **patterns) -> str:
        """Substitute patterns until no more substitutions are possible."""
        return last(
            self.subber(self._root, **(self._templates | patterns)), default=self._root
        )

    def subber(self, result: str, **patterns) -> Iterator[str]:
        """Substitute patterns, yielding intermediate values."""
        while result != (result := Template(result).substitute(patterns)):
            yield result

    def __getitem__(self, key: str) -> str:
        return self._templates[key]

    def __setitem__(self, key: str, pattern: str):
        self._templates[key] = pattern
        setattr(self.ns, key, pattern)

    def __delitem__(self, key: str):
        return super().__delitem__(key)

    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def __len__(self) -> int:
        return len(self._templates)


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern with baked-in `^` and `$`."""
    return compile(flags=VERBOSE | MULTILINE, pattern=f"^{pattern}$")
