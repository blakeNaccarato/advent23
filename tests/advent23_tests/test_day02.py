from advent23_tests import parametrize

DAY = "02"
USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected


USER = "blake"


@parametrize(USER, DAY)
def test_blake(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected
