"""Helper functions for tests."""

from pathlib import Path
from typing import NamedTuple

from boilercore.notebooks.namespaces import NO_PARAMS, Params


class NsArgs(NamedTuple):
    """Indirect parameters for notebook namespace fixture."""

    nb: Path
    params: Params = NO_PARAMS
