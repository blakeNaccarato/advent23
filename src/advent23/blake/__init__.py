"""Blake's solutions."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from copy import deepcopy
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from textwrap import fill
from types import SimpleNamespace
from typing import Self
from warnings import warn


def remap(**kwds: Stringer | str) -> Pattern[str]:
    """Multiline, verbose regex pattern compile from a `Stringer` mapping."""
    return rem(Stringer(**kwds).sub())


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, **kwds: Self | str):
        if "root" not in kwds:
            raise ValueError("Stringer missing `root` key.")
        _ns = SimpleNamespace()
        _dict: dict[str, Self | str] = _ns.__dict__
        super().__setattr__("_ns", _ns)
        super().__setattr__("_dict", _dict)
        for k, v in kwds.items():
            if isinstance(k, Stringer) or not isinstance(k, Mapping):
                self._dict[k] = v  # type: ignore
            else:
                self._dict[k] = Stringer(**v)  # type: ignore
        super().__init__()

    def sub(self, quiet: bool = False) -> str:
        root = root.sub() if isinstance(root := self.root, Stringer) else root
        while root != (root := self.rsub(root, quiet)):
            pass
        return root.replace("$$", "$")

    def rsub(self, child: Self | str, quiet: bool) -> str:
        return Template(child.replace("$$", "$$$$")).substitute(  # type: ignore
            {
                k: self.rsub(v, quiet) if isinstance(v, Stringer) else v
                for k, v in self.items()
            }
        )

    def __repr__(self) -> str:
        args = ", ".join([f"{k}={v!r}" for k, v in self.items()])
        return fill(f"{Stringer.__name__}({args})", width=88, subsequent_indent=" " * 4)

    def __setattr__(self, name: str, value: Self | str):
        self[name] = value

    def __getattr__(self, name: str):
        return self[name]

    def __setitem__(self, key: str, value: Self | str):
        if not key.isidentifier():
            raise ValueError("Invalid identifier.")
        self._dict[key] = value  # type: ignore

    def __getitem__(self, key: str) -> Self | str:  # type: ignore
        return self._dict[key]  # type: ignore

    def __delitem__(self, key: str):
        if key == "root":
            raise KeyError("Cannot delete root.")
        del self._dict[key]  # type: ignore

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __ror__(self, other: Mapping[str, str]) -> Self:
        return self | other

    def __or__(self, other: Self | Mapping[str, str]) -> Self:
        return deepcopy(self).__ior__(other)

    def __ior__(self, other: Self | Mapping[str, str]) -> Self:
        self._dict.update(other)  # type: ignore
        return self

    def __copy__(self) -> Self:
        warn("Shallow copy not possible, returning deep copy.", stacklevel=2)
        return deepcopy(self)

    def __deepcopy__(self, _memo) -> Self:
        return Stringer(**self)  # type: ignore
