from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md, md_links=True))


def test_markdown_path():
    md = "[test](foo.md)"
    gem = "=> foo.gmi test"
    assert f(md) == gem


def test_markdown_path_anchor():
    md = "[test](foo.md#bar)"
    gem = "=> foo.gmi test"
    assert f(md) == gem
