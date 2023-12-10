"""Blake's solutions."""

from collections.abc import Iterator, MutableMapping
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from typing import Self


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, **subs: Self | str):
        self.subs = subs
        super().__init__()

    def sub(self) -> str:
        root: str = self.subs["root"]  # type: ignore
        while root != (root := self.sub_child(root)):
            pass
        return root.replace("$$", "$")

    def sub_child(self, child: str | Self) -> str:
        return Template(child.replace("$$", "$$$$")).substitute(  # type: ignore
            {
                name: child if isinstance(child, str) else self.sub_child(child)
                for name, child in self.items()
            }
        )

    def __getitem__(self, key: str) -> Self | str:  # type: ignore
        return self.subs[key]

    def __setitem__(self, key: str, sub: Self | str):
        self.subs[key] = sub

    def __delitem__(self, key: str):
        del self.subs[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.subs)

    def __len__(self) -> int:
        return len(self.subs)


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)
