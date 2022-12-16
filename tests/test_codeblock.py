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


def test_nested_fences():
    md = """
```
    spaces should be preserved
    ```
    even in here
    there will be two lines
    ```
    and still preserved, as that fence should not end the block
```
And now the block has ended.
This line should be eaten. (note -1 below)
"""
    assert len(md.splitlines()) - 1 == len(f(md).splitlines())


def test_nested_fences_in_lists():
    md = """
1.  This item will have a fence.
    ```
    This is the fence.
    And this line shall be preserved.
        ```begin nested fence
        nested fence
        content
        ```
    Continue preserving newlines.
    ```
2.  This item has no fence
"""
    assert len(md.splitlines()) == len(f(md).splitlines())


def test_nested_fences_in_lists_uneven():
    md = """
1.  This item will have a fence.
    `````
    This is the fence.
    And this line shall be preserved.
        ```begin nested fence
        nested fence
        content
        ````
    Continue preserving newlines.
    ````````````````
2.  This item has no fence
"""
    assert len(md.splitlines()) == len(f(md).splitlines())


def test_nested_fences_in_lists_uneven():
    md = """
1.  This item will have a fence.
    ~~~~~
    This is the fence.
    And this line shall be preserved.
        ```begin nested fence
        nested fence
        content
        ```
    Continue preserving newlines.
    ~~~~~~~~~~~~~~~~
2.  This item has no fence
"""
    assert len(md.splitlines()) == len(f(md).splitlines())
