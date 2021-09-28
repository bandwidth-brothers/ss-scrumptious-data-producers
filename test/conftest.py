import pytest


@pytest.fixture
def test_kwargs():
    class TestKwargs(object):
        def __call__(self, **kwargs):
            self.args = kwargs
    return TestKwargs()
