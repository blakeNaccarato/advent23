"""Stronger string processing with stringers."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import chain
from re import NOFLAG, Pattern, RegexFlag, compile
from string import Template
from textwrap import fill
from types import SimpleNamespace
from typing import Any, Self, TypeAlias

from IPython.core.display import Markdown
from IPython.display import display

from advent23 import CheckDict, disp_name, make_readable


def g(N: str, P: str = r".+", **kwds) -> dict[str, Stringer]:  # noqa: N803
    """Named capturing group for unpacking into a Stringer.

    Args:
        N: Name of the capturing group.
        P: Pattern to match.
        kwds: Other keyword arguments for `Stringer`.
    """
    return {N: Stringer(r"(?P<$N>$P)", N=N, P=P, **kwds)}


class Stringer(MutableMapping[str, Self | str]):
    def __init__(
        self,
        root: Self | str | Mapping[str, Self | str] = "",
        **kwds: Self | str | Mapping[str, Self | str],
    ):
        """Recursive string substitution template."""
        super().__init__()
        self._ns = SimpleNamespace()
        for k, v in ({"root": root} | kwds).items():
            self[k] = v if isinstance(v, type(self) | str) else Stringer(**v)  # type: ignore
        self._flags = NOFLAG

    def pat(self, quiet: bool = False, flags: RegexFlag = NOFLAG) -> Pattern[str]:
        """Substitute values into root `r` and get compiled regex pattern."""
        return compile(self.sub(quiet), flags=self._flags | flags)

    def set_flags(self, flags: RegexFlag) -> Self:
        """Set regex flags for pattern compilation."""
        self._flags = flags
        return self

    def sub(self, quiet: bool = False, final: bool = True) -> str:
        """Substitute values into root `r`."""
        node: str = self.root  # type: ignore
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
        if name in {"_ns", "_flags"}:
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
        if name == "root":
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


StringerCheck = Callable[[Stringer], Any]
StringerChecks: TypeAlias = MutableMapping[str, StringerCheck]

NO_CHECKS = {}


@dataclass
class StringerChecker:
    chk: CheckDict
    stringer: Stringer
    checks: StringerChecks = field(default_factory=dict)

    def __post_init__(self):
        self(self.stringer, disp=False, **self.checks)

    def __call__(
        self, stringer: Stringer, disp: bool = True, **kwds: StringerCheck
    ) -> Stringer:
        """Run checks and return the `Stringer` that passed them.

        Args:
            stringer: Stringer to substitute, compile, and check.
            disp: Whether to display the compiled pattern.
            kwds: Checks to add if existing checks pass.
        """
        if disp:
            disp_name("pattern", stringer.pat())
        if all(
            self.check(stringer, name, check)
            for name, check in chain.from_iterable([self.checks.items(), kwds.items()])
        ):
            return stringer
        else:
            raise ValueError("Some checks failed.")

    def check(self, stringer: Stringer, name: str, check: StringerCheck) -> bool:
        result = check(stringer)
        if expected := self.chk.get(name):
            try:
                assert result == expected  # noqa: S101
            except AssertionError:
                display(Markdown(f'### "{make_readable(name)}" check failed'))
                disp_name("Expected", self.chk[name])
                disp_name("Your answer", result)
                raise
        self.chk[name] = result
        return True
