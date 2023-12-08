from advent23_tests.parametrizations import parametrize, walk_ex, walk_other, walk_self


@parametrize(walk_self)
def test_self(ans, exp):
    assert ans == exp


@parametrize(walk_other)
def test_other(ans, exp):
    assert ans == exp


@parametrize(walk_ex)
def test_ex(ans, exp):
    assert ans == exp
