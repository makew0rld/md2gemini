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


def test_links_in_lists():
    # https://github.com/makeworld-the-better-one/md2gemini/issues/30

    md = "* before [bar](/foo) after \n* next item"
    gem = """
* before 
=> /foo bar
after
* next item
    """.strip()

    assert f(md, "newline") == gem

    md = "* before [bar](/foo) after \n* next item"
    gem = """
* before bar after
* next item

=> /foo bar
    """.strip()

    assert f(md, "copy") == gem
