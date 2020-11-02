from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md, plain=True))


def test_empty_input():
    md = ""
    gem = ""
    assert f(md) == gem


def test_remove_bold():
    md = "Sentence with **bold** in it."
    gem = "Sentence with bold in it."
    assert f(md) == gem


def test_remove_bold_2():
    md = "Sentence with __bold__ in it."
    gem = "Sentence with bold in it."
    assert f(md) == gem


def test_remove_italics():
    md = "Sentence with *italics* in it."
    gem = "Sentence with italics in it."
    assert f(md) == gem


def test_remove_italics_2():
    md = "Sentence with _italics_ in it."
    gem = "Sentence with italics in it."
    assert f(md) == gem


def test_remove_inline_html():
    md = "<i>test1</i> <b>test2</b> <em>test3</em> <made-up>test4</made-up>"
    gem = "test1 test2 test3 test4"
    assert f(md) == gem


def test_convert_html_block():
    # Not actually specific to plain=True
    md = "<div>\n<tag>html is here</tag>\n</div>\n\nText after"
    gem = "```html\n<div>\n<tag>html is here</tag>\n</div>\n```\n\nText after"
    assert f(md) == gem
