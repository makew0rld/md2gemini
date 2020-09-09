from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md))


def test_no_extra_newline():
    md = "Non code block\n\n    code block here\n\nMore non code"
    gem = "Non code block\n\n```\ncode block here\n```\n\nMore non code"
    assert f(md) == gem


def test_with_extra_newline():
    md = "Non code block\n\n    code block here\n\n\nMore non code"
    gem = "Non code block\n\n```\ncode block here\n\n```\n\nMore non code"
    assert f(md) == gem


def test_ends_with_no_newlines():
    md = "Non code block\n\n    code block here"
    gem = "Non code block\n\n```\ncode block here\n```"
    assert f(md) == gem
