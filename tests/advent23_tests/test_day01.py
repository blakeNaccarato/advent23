from advent23_tests import parametrize, parametrize_compare

DAY = "01"
USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ans, exp):
    assert ans == exp


@parametrize(USER, DAY, others=True)
def test_abdul_others(ans, exp):
    assert ans == exp


USER = "blake"


@parametrize(USER, DAY)
def test_blake(ans, exp):
    assert ans == exp


@parametrize(USER, DAY, others=True)
def test_blake_others(ans, exp):
    assert ans == exp


USER = "brad"


@parametrize(USER, DAY)
def test_brad(ans, exp):
    assert ans == exp


@parametrize(USER, DAY, others=True)
def test_brad_others(ans, exp):
    assert ans == exp


@parametrize_compare("brad", "blake", DAY)
def test_brad_blake(ans, exp):
    assert ans == exp
