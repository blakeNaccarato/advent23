"""Blake's solutions."""

from re import MULTILINE, VERBOSE, Pattern, compile


def rem(pattern: str) -> Pattern[str]:
    """Multiline, verbose, compiled regex pattern with baked-in `^` and `$`."""
    return compile(flags=VERBOSE | MULTILINE, pattern=f"^{pattern}$")
