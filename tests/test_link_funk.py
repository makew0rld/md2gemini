from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md, link_func=(lambda x: "foo")))


def test_func_root_url():
    md = "[test](/url)"
    gem = "=> foo test"
    assert f(md) == gem


def test_func_absolute_url():
    md = "[test](https://duck.com/test)"
    gem = "=> foo test"
    assert f(md) == gem
