"""Blake's solutions."""

from collections.abc import Iterator, MutableMapping
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template


class Stringer(MutableMapping[str, str]):
    def __getitem__(self, __key: str) -> str:
        return super().__getitem__(__key)

    def __setitem__(self, key: str, pattern: str) -> None:
        return super().__setitem__(key, pattern)

    def __delattr__(self, __name: str) -> None:
        return super().__delattr__(__name)

    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def __len__(self) -> int:
        return super().__len__()


def tsub(_root: str = "root", **patterns: str) -> str:
    """Substitute patterns until no more substitutions are possible."""
    result = patterns[_root]
    while result != (result := Template(result).substitute(patterns)): ...
    return result


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern with baked-in `^` and `$`."""
    return compile(flags=VERBOSE | MULTILINE, pattern=f"^{pattern}$")
