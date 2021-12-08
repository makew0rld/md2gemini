from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md))


def test_single_line_quote():
    md = "> test quote"
    gem = md
    assert f(md) == gem


def test_multiline_quote():
    md = "> test quote\n>test again\n>  third time"
    gem = "> test quote\n> test again\n> third time"
    assert f(md) == gem


def test_quote_with_hard_linebreaks():
    # https://github.com/makeworld-the-better-one/md2gemini/issues/32

    md = """
> What is a good man?  
> A teacher of a bad man.  
> What is a bad man?  
> A good man's charge.
"""

    gem = """
> What is a good man?
> A teacher of a bad man.
> What is a bad man?
> A good man's charge.
""".strip()

    assert f(md) == gem


def test_quote_with_text_after():
    # https://github.com/makeworld-the-better-one/md2gemini/issues/31

    md = """
> some quote

More text
    """

    gem = """
> some quote

More text
    """.strip()

    assert f(md) == gem
