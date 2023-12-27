"""Stronger string processing with stringers."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping
from copy import deepcopy
from dataclasses import dataclass, field
from re import NOFLAG, Match, Pattern, RegexFlag, compile
from string import Template
from textwrap import fill
from types import SimpleNamespace
from typing import Any, Self

from IPython.core.display import Markdown
from IPython.display import display

from advent23 import CheckDict, disp_name, make_readable

ANY = r"(?:.|\n)"
"""Any character, including newlines."""
PAT = rf"{ANY}+"
"""Any non-zero-length string."""


class Stringer(MutableMapping[str, Self]):
    def __init__(self, root=PAT, **kwds):
        """Recursive string substitution template."""
        super().__init__()
        self._ns = SimpleNamespace()
        for k, v in ({"root": root} | kwds).items():
            self[k] = v if isinstance(v, type(self) | str) else type(self)(**v)
        self._flags = NOFLAG

    def compile(self, quiet: bool = False, flags: RegexFlag = NOFLAG) -> Pattern[str]:  # noqa: A003
        """Substitute values into root `r` and get compiled regex pattern."""
        return compile(self.sub(quiet), flags=self._flags | flags)

    def set_flags(self, flags: RegexFlag) -> Self:
        """Set regex flags for pattern compilation."""
        self._flags = flags
        for k, v in self.items():
            if isinstance(v, type(self)):
                self[k].set_flags(flags)
        return self

    def sub(self, quiet: bool = False, final: bool = True) -> str:
        """Substitute values into root `r`."""
        root = self.root
        node: str = root.sub(quiet) if isinstance(root, type(self)) else root
        while node != (
            node := self.get_tsub(node, quiet)({
                name: child.sub(quiet, final=False)
                if isinstance(child, Stringer)
                else child
                for name, child in self.items()
            })
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

    def __setattr__(self, name: str, value):
        if "_" in name:
            return super().__setattr__(name, value)
        self._ns.__setattr__(name, value)

    def __getattr__(self, name: str):
        if name == "_ns":
            return super().__getattr__(name)  # type: ignore
        return self._ns.__getattribute__(name)

    def __setitem__(self, key: str, value):
        self._ns.__setattr__(key, value)

    def __getitem__(self, name: str):
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
        self.update(other)
        return self


def group(
    pat: Stringer | str = PAT, name: str = "", **kwds
) -> dict[str, GroupStringer]:
    """Named substitution with named capturing group for unpacking into a Stringer.

    Args:
        pat: Pattern to match.
        name: Name for this substitution and the named capturing-group.
        kwds: Other substitutions.
    """
    return {name: GroupStringer(pat, name, **kwds)}


class GroupStringer(Stringer):
    def __init__(self, pat: Stringer | str = PAT, name: str = "", **kwds):
        """Stringer with a non-capturing group or a named capturing group.

        Args:
            pat: Pattern to match.
            name: If given, name for the named capturing-group.
            kwds: Other substitutions.
        """
        if name:
            super().__init__(r"(?P<$name>$pat)", pat=pat, name=name, **kwds)
        else:
            super().__init__(r"(?:$pat)", pat=pat, **kwds)


StringerCheck = Callable[[Stringer], Any]


@dataclass
class StringerChecker:
    chk: CheckDict
    stringer: Stringer = field(default_factory=Stringer)
    checks: dict[str, StringerCheck] = field(default_factory=dict)

    def __call__(self, stringer: Stringer, **kwds: StringerCheck) -> Stringer:
        """Run checks and return the `Stringer` that passed them.

        Args:
            stringer: Stringer to substitute, compile, and check.
            disp: Whether to display the compiled pattern.
            kwds: Checks to add if existing checks pass.
        """
        disp_name("stringer", stringer)
        disp_name("pattern", stringer.compile())
        for name in [n for n in self.checks if n not in kwds]:
            self.check(stringer, name, self.checks[name], update=False)
        for name in kwds:
            self.check(stringer, name, kwds[name], update=True)
        self.checks |= kwds
        self.stringer = stringer
        return self.stringer

    def check(
        self, stringer: Stringer, name: str, check: StringerCheck, update: bool = True
    ):
        try:
            result = check(stringer)
        except Exception:
            display(Markdown(f'### "{make_readable(name)}" check raised exception'))
            raise
        if update:
            self.chk[name] = result
            return
        if expected := self.chk.get(name):
            try:
                if isinstance(result, Match) and isinstance(expected, Match):
                    assert check_match(result, expected)  # noqa: S101
                else:
                    assert result == expected  # noqa: S101
            except AssertionError:
                display(Markdown(f'### "{make_readable(name)}" check failed'))
                disp_name("Expected", self.chk[name])
                disp_name("Your answer", result)
                raise
        self.chk[name] = result


def check_match(match: Match[str], other: Match[str]) -> bool:
    return (
        match.group() == other.group()
        and match.groups() == other.groups()
        and match.groupdict() == other.groupdict()
    )
