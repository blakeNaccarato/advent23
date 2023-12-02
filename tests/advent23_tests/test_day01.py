from advent23_tests import parametrize

DAY = "01"

USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected


@parametrize(USER, DAY, reverse=True)
def test_abdul_reverse(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected


USER = "blake"


@parametrize(USER, DAY)
def test_blake(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected


@parametrize(USER, DAY, reverse=True)
def test_blake_reverse(ns, expected):
    """Tests for Abdul's puzzle answers."""
    assert ns.ANS == expected
