import pytest

from stalehand.env.browser import BrowserEnv


@pytest.fixture(scope="module")
def env():
    e = BrowserEnv()
    yield e
    e.close()
