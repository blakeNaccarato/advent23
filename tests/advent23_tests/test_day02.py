from advent23_tests import parametrize

DAY = "02"
USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ans, exp):
    assert ans == exp


USER = "blake"


@parametrize(USER, DAY, check=True)
def test_blake_checks(ans, exp):
    assert ans == exp


@parametrize(USER, DAY)
def test_blake(ans, exp):
    assert ans == exp
