"""Stronger string processing with stringers."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping
from copy import deepcopy
from dataclasses import dataclass, field
from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template
from textwrap import fill
from types import SimpleNamespace
from typing import Any, Self
from warnings import warn

from IPython.core.display import Markdown
from IPython.display import display

from advent23 import NO_CHECKS, CheckDict, PatternChecks, disp_name, make_readable


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


def g(N: str, P: str = r".+", **kwds) -> dict[str, Stringer]:  # noqa: N803
    """Named capturing group for unpacking into a Stringer.

    Args:
        N: Name of the capturing group.
        P: Pattern to match.
        kwds: Other keyword arguments for `Stringer`.
    """
    return {N: Stringer(r=r"(?P<$N>$P)", N=N, P=P, **kwds)}


@dataclass
class StringerChecker:
    chk: CheckDict
    checks: PatternChecks = field(default_factory=dict)

    def __call__(self, stringer: Stringer, also: PatternChecks = NO_CHECKS) -> Stringer:
        """Run checks and return the `Stringer` that passed them.

        Args:
            stringer: Stringer to substitute, compile, and check.
            also: Checks to assign if existing checks pass.
        """
        pattern = remap(stringer)
        disp_name("pattern", pattern.pattern)
        for name, check in self.checks.items():
            if name not in self.chk:
                continue
            try:
                check(pattern)
            except:  # noqa: E722
                warn(f'Checkpoint "{name}" failed.', stacklevel=2)
        for name, check in also.items():
            try:
                result = check(pattern)
                self.checks[name] = check
                self.chk[name] = result
            except:  # noqa: E722
                warn(f'Checkpoint "{name}" failed.', stacklevel=2)
        return stringer

    def check(self, name: str, ans):
        try:
            expected = self.chk[name]
        except KeyError as err:
            raise KeyError(f'Checkpoint "{name}" not found.') from err
        try:
            assert ans == expected  # noqa: S101
        except AssertionError:
            display(Markdown(f'### "{make_readable(name)}" check failed'))
            disp_name("Expected", self.chk[name])
            disp_name("Your answer", ans)
            raise


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
                self[k] = Stringer(**v)  # type: ignore

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
