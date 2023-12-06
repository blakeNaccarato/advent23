from advent23_tests import COMPARE_USER, parametrize, parametrize_compare

DAY = "01"
USER = "blake"


@parametrize(USER, DAY)
def test_blake(ans, exp):
    assert ans == exp


USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ans, exp):
    assert ans == exp


@parametrize_compare(USER, COMPARE_USER, DAY)
def test_abdul_blake(ans, exp):
    assert ans == exp


USER = "brad"


@parametrize(USER, DAY)
def test_brad(ans, exp):
    assert ans == exp


@parametrize_compare(USER, COMPARE_USER, DAY)
def test_brad_blake(ans, exp):
    assert ans == exp
