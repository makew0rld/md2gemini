from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md, base_url="https://example.com/"))


def test_root_url():
    md = "[test](/url)"
    gem = "=> https://example.com/url test"
    assert f(md) == gem


def test_absolute_url():
    md = "[test](https://duck.com/test)"
    gem = "=> https://duck.com/test test"
    assert f(md) == gem
