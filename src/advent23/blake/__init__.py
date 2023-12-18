"""Blake's solutions."""

from re import MULTILINE

from advent23.stringers import GroupStringer

LINE_STRINGER = GroupStringer("line").set_flags(MULTILINE)
"""Custom stringer with a `line` root group matching anything on a line."""
