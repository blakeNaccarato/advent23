from advent23_tests import parametrize

DAY = "01"
USER = "abdul"


@parametrize(USER, DAY)
def test_abdul(ans, exp):
    assert ans == exp


@parametrize(USER, DAY, other_user="blake")
def test_abdul_others(ans, exp):
    assert ans == exp


USER = "blake"


@parametrize(USER, DAY)
def test_blake(ans, exp):
    assert ans == exp


@parametrize(USER, DAY, other_user="abdul")
def test_blake_others(ans, exp):
    assert ans == exp
