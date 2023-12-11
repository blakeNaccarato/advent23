"""Blake's solutions."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from copy import deepcopy
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from types import SimpleNamespace
from typing import Self
from warnings import warn


def remvs(**kwds: Stringer | str) -> Pattern[str]:
    return remv(Stringer(**kwds).sub())


def remv(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, **kwds: Self | str):
        if "root" not in kwds:
            raise ValueError("Stringer missing `root` key.")
        self._ns = SimpleNamespace(
            **{k: v if isinstance(v, str) else type(self)(**v) for k, v in kwds.items()}
        )
        super().__init__()

    def sub(self) -> str:
        root = root.sub() if isinstance(root := self["root"], type(self)) else root
        while root != (root := self.rsub(root)):  # type: ignore
            pass
        return root.replace("$$", "$")

    def rsub(self, child: str | Self) -> str:
        return Template(child.replace("$$", "$$$$")).substitute(
            {k: v if isinstance(v, str) else self.rsub(v) for k, v in self.items()}
        )

    @property
    def _dict(self) -> dict[str, Self | str]:
        return self._ns.__dict__

    def __repr__(self) -> str:
        args = ", ".join([f"{k}={repr(v)}" for k, v in self.items()])  # noqa: RUF010  # Doesn't work when `repr(v)` is `v!r`
        return f"{type(self).__name__}({args})"

    def __getattribute__(self, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)
        return getattr(self._ns, name, None) or super().__getattribute__(name)

    def __setattr__(self, name: str, value):
        if name == "ns" or name.startswith("_"):
            return super().__setattr__(name, value)
        setattr(self._ns, name, value)

    def __ror__(self, other: Mapping[str, str]) -> Self:
        return self | other

    def __or__(self, other: Self | Mapping[str, str]) -> Self:
        return deepcopy(self).__ior__(other)

    def __ior__(self, other: Self | Mapping[str, str]) -> Self:
        self._dict.update(other._dict if isinstance(other, type(self)) else other)
        return self

    def __copy__(self) -> Self:
        warn("Shallow copy not possible, returning deep copy.", stacklevel=2)
        return deepcopy(self)

    def __deepcopy__(self, memo: dict[int, Self]) -> Self:
        return type(self)(**self)

    def __getitem__(self, key: str) -> Self | str:  # type: ignore
        return self._dict[key]

    def __setitem__(self, key: str, sub: Self | str):
        self._dict[key] = sub

    def __delitem__(self, key: str):
        del self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)
