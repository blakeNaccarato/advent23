from advent23_tests import OTHER, parametrize, parametrize_ex, parametrize_other

DAY = "01"
USER = "blake"


@parametrize(USER, DAY)
def test_blake(ans, exp):
    assert ans == exp


@parametrize_ex(USER, DAY)
def test_blake_ex(ans, exp):
    assert ans == exp


USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ans, exp):
    assert ans == exp


@parametrize_ex(USER, DAY)
def test_abdul_ex(ans, exp):
    assert ans == exp


@parametrize_other(USER, DAY, OTHER)
def test_abdul_other(ans, exp):
    assert ans == exp


USER = "brad"


@parametrize(USER, DAY)
def test_brad(ans, exp):
    assert ans == exp


@parametrize_ex(USER, DAY)
def test_brad_ex(ans, exp):
    assert ans == exp


@parametrize_other(USER, DAY, OTHER)
def test_brad_other(ans, exp):
    assert ans == exp
