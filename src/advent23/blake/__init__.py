"""Blake's solutions."""

from re import MULTILINE

from advent23.stringers import Stringer, g

LINE_STRINGER = Stringer(r"^$line$$", **g("line")).set_flags(MULTILINE)
"""Custom stringer with a `line` root group matching anything on a line."""
