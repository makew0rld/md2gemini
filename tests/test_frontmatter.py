from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md, frontmatter=True))


def test_remove_frontmatter_jekyll():
    md = "---\nsome text\n---\nbeginning"
    gem = "beginning"
    assert f(md) == gem


def test_remove_frontmatter_zola():
    md = "+++\nsome text\n+++\nbeginning"
    gem = "beginning"
    assert f(md) == gem


def test_no_remove_frontmatter_jekyll():
    # "Frontmatter" doesn't have an end
    md = "---\nsome text"
    assert f(md).endswith("some text")


def test_no_remove_frontmatter_zola():
    # "Frontmatter" doesn't have an end
    md = "+++\nsome text"
    gem = "+++ some text"
    assert f(md) == gem
