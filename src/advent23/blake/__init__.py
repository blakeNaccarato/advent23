"""Blake's solutions."""

from re import MULTILINE, VERBOSE, Pattern, compile
from string import Template


def tsub(_root: str = "root", **patterns: str) -> str:
    """Substitute patterns until no more substitutions are possible."""
    result = patterns[_root]
    while result != (result := Template(result).substitute(patterns)): ...
    return result


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern with baked-in `^` and `$`."""
    return compile(flags=VERBOSE | MULTILINE, pattern=f"^{pattern}$")
