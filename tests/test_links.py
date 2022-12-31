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

    md = "* 1before [bar](/foo) after \n* next item"
    gem = """
* 1before 
=> /foo bar
after
* next item
    """.strip()

    assert f(md, "newline") == gem

    md = "* 2before [bar](/foo) after \n* next item"
    gem = """
* 2before bar after
* next item

=> /foo bar
    """.strip()

    assert f(md, "copy") == gem


def test_many_footnote_links():
    md = """
* [foo](foo.md)

# headline

* [bar](bar.md)
* [bar2](bar2.md)

Some text after

* [foo2](foo2.md)
    """

    gem = """
* foo[1]

=> foo.md 1: foo.md

# headline

* bar[2]
* bar2[3]

=> bar.md 2: bar.md
=> bar2.md 3: bar2.md

Some text after

* foo2[4]

=> foo2.md 4: foo2.md
""".strip()

    assert f(md, links="paragraph") == gem


def test_link_in_quote():
    # https://github.com/makeworld-the-better-one/md2gemini/issues/44

    md = """
Text before

> quote with [link](https://example.com) in it

Text after
    """

    gem = """
Text before

> quote with link[1] in it

=> https://example.com 1: https://example.com

Text after
    """.strip()

    assert f(md, links="paragraph") == gem


def test_link_in_quote_newline():
    # https://github.com/makeworld-the-better-one/md2gemini/issues/44

    md = """
Text before

> quote with newline link in it
>
> [link](https://example.com)

Text after
    """

    gem = """
Text before

> quote with newline link in it
> 
> link[1]

=> https://example.com 1: https://example.com

Text after
    """.strip()

    assert f(md, links="paragraph") == gem
