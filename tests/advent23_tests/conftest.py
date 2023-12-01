"""Test configuration."""

from types import SimpleNamespace

import pytest
from boilercore import WarningFilter, filter_certain_warnings
from boilercore.notebooks.namespaces import get_cached_minimal_nb_ns
from boilercore.testing import unwrap_node

from advent23_tests import NsArgs

# * -------------------------------------------------------------------------------- * #
# * Autouse


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings(
        [
            WarningFilter(
                message=r"numpy\.ndarray size changed, may indicate binary incompatibility\. Expected \d+ from C header, got \d+ from PyObject",
                category=RuntimeWarning,
            ),
            WarningFilter(
                message=r"A grouping was used that is not in the columns of the DataFrame and so was excluded from the result\. This grouping will be included in a future version of pandas\. Add the grouping as a column of the DataFrame to silence this warning\.",
                category=FutureWarning,
            ),
        ]
    )


# * -------------------------------------------------------------------------------- * #
# * Notebook namespaces


@pytest.fixture()
def ns(request) -> SimpleNamespace:
    """Notebook namespace."""
    namespace: NsArgs = request.param
    return get_cached_minimal_nb_ns(
        nb=namespace.nb.read_text(encoding="utf-8"),
        receiver=unwrap_node(request.node),
        params=namespace.params,
    )
