from functools import partial
from types import SimpleNamespace
from typing import Any, TypeAlias

from boilercore.notebooks.namespaces import (
    NO_ATTRS,
    Attributes,
    get_nb_client,
    parametrize_notebook,
)
from cachier import cachier

from advent23_tests.hashes import hash_args_PATCHED

Params: TypeAlias = dict[str, Any]
"""Notebook parameters."""


ATTRIUTES = ["chk", "inp"]
"""Attributes to include in notebook namespaces for tests.

Not all notebook attributes are guaranteed pickleable, even with `dill`, and we can't
look ahead to see if it'll pickle properly, so let's just get the attributes we know
should pickle successfully.

We could compose a list of pickleable attributes by looking at `dill`'s dispatch table
and documentation.
"""

NO_PARAMS = {}
"""No notebook parameters."""


def get_nb_ns_PATCHED(  # noqa: N802
    nb: str, params: Params = NO_PARAMS, attributes: Attributes = NO_ATTRS
) -> SimpleNamespace:
    """Get notebook namespace, optionally parametrizing it."""
    nb_client = get_nb_client(nb)
    if params:
        parametrize_notebook(nb_client._nb, parameters=params)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
    namespace = nb_client.get_namespace()
    return SimpleNamespace(
        **(
            {attr: namespace[attr] for attr in attributes if namespace.get(attr)}
            if attributes
            else namespace
        )
    )


@cachier(hash_func=partial(hash_args_PATCHED, get_nb_ns_PATCHED))
def get_cached_nb_ns(nb: str, params: Params = NO_PARAMS) -> SimpleNamespace:
    """Get cached minimal namespace suitable for passing to a receiving function."""
    return get_nb_ns_PATCHED(nb, params, attributes=ATTRIUTES)
