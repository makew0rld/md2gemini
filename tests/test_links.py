from .util import normalize
from md2gemini import md2gemini


def f(md, links):
    return normalize(md2gemini(md, links=links))


def test_paragraph_links():
    md = """
* [foo](foo.md)

# headline

* [bar](bar.md)
    """

    gem = """
* foo[1]

=> foo.md 1: foo.md

# headline

* bar[2]


=> bar.md 2: bar.md
""".strip()

    assert f(md, links="paragraph") == gem
