"""Blake's solutions."""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from copy import deepcopy
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from typing import Any, Self

NO_MAPPING = {}


def remvs(root: str = "", **kwds: Stringer | str) -> Pattern[str]:
    return remv(stringup(**({"root": root} if root else {}), **kwds).sub())


def stringup(
    mapping: MutableMapping[str, Any] = NO_MAPPING, /, **kwds: Any
) -> Stringer:
    return Stringer(
        {
            name: stringup(sub) if isinstance(sub, MutableMapping) else sub
            for name, sub in (mapping or kwds).items()
        }
    )


def remv(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)


class Stringer(MutableMapping[str, Self | str]):
    def __init__(
        self,
        mapping: MutableMapping[str, Self | str] = NO_MAPPING,
        /,
        **kwds: Self | str,
    ):
        self.subs = mapping or kwds
        if "root" not in self.subs:
            raise ValueError("Stringer missing `root` key.")
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

    def __repr__(self) -> str:
        return f"{super().__repr__()}\nSubs: {self.subs!r}"

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

    def __or__(self, other: Self) -> Self:
        self = deepcopy(self)
        self.subs.update(other.subs)
        return self

    def __ior__(self, other: Self) -> Self:
        return self.__or__(other)