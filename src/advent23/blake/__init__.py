"""Blake's solutions."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping
from copy import deepcopy
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from textwrap import fill
from types import SimpleNamespace
from typing import Any, Self


def remap(
    stringer: Stringer | None = None,
    /,
    **kwds: Stringer | str | Mapping[str, Stringer | str],
) -> Pattern[str]:
    """Multiline, verbose regex pattern compile from a `Stringer` mapping."""
    return rem((stringer or Stringer(**kwds)).sub())


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern."""
    return compile(flags=VERBOSE | MULTILINE, pattern=pattern)


class Stringer(MutableMapping[str, Self | str]):
    def __init__(self, **kwds: Self | str | Mapping[str, Self | str]):
        """Recursive string substitution template."""
        super().__init__()
        if "r" not in kwds:
            raise ValueError("Stringer missing root key `r`.")
        self._ns = SimpleNamespace()
        for k, v in kwds.items():
            if isinstance(v, type(self) | str):
                self[k] = v
            else:
                self[k] = Stringer(**v)

    def sub(self, quiet: bool = False, final: bool = True) -> str:
        """Substitute values into root `r`."""
        node: str = self.r  # type: ignore
        while node != (
            node := self.get_tsub(node, quiet)(
                {
                    name: child.sub(quiet, final=False)
                    if isinstance(child, Stringer)
                    else child
                    for name, child in self.items()
                }
            )
        ):
            pass
        return node.replace("$$", "$") if final else node

    def get_tsub(self, string: str, quiet: bool) -> Callable[[Mapping[str, str]], str]:
        """Get a template substituter that raises exceptions or passes silently."""
        t = Template(string.replace("$$", "$$$$"))
        return t.safe_substitute if quiet else t.substitute

    def __repr__(self) -> str:
        args = ", ".join([f"{k}={v!r}" for k, v in self.items()])
        return fill(f"{Stringer.__name__}({args})", width=88, subsequent_indent=" " * 4)

    def __setattr__(self, name: str, value: Self | str):
        if name == "_ns":
            return super().__setattr__(name, value)
        self._ns.__setattr__(name, value)

    def __getattr__(self, name: str) -> Self | str:
        if name == "_ns":
            return super().__getattr__(name)  # type: ignore
        return self._ns.__getattribute__(name)

    def __setitem__(self, key: str, value: Self | str):
        self._ns.__setattr__(key, value)

    def __getitem__(self, name: str) -> Self | str:  # type: ignore
        return self._ns.__getattribute__(name)

    def __delitem__(self, name: str):
        if name == "r":
            raise KeyError("Cannot delete root.")
        self._ns.__delattr__(name)

    def __iter__(self) -> Iterator[Self | str]:  # type: ignore
        return iter(self._ns.__dict__)

    def __len__(self) -> int:
        return len(self._ns.__dict__)

    def __ror__(self, other: Mapping[str, Any]) -> Self:
        return self | other

    def __or__(self, other: Self | Mapping[str, Any]) -> Self:
        return deepcopy(self).__ior__(other)

    def __ior__(self, other: Self | Mapping[str, Any]) -> Self:
        self.update(other)  # type: ignore
        return self
