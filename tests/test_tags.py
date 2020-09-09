from .util import normalize
from md2gemini import md2gemini
import pytest

multiple_tags = pytest.fixture(params=["[IMG]", "IMG", "test", "AAA"])


@multiple_tags
def img_tag_no_text(request):
    md = "![](image.jpg)"
    gem = "=> image.jpg " + request.param
    assert normalize(md2gemini(md, img_tag=request.param)) == gem


def test_img_tag_no_text(img_tag_no_text):
    pass


@multiple_tags
def img_tag_with_text(request):
    md = "![text](image.jpg)"
    gem = "=> image.jpg text " + request.param
    assert normalize(md2gemini(md, img_tag=request.param)) == gem


def test_img_tag_with_text(img_tag_with_text):
    pass


def test_empty_img_tag_no_text():
    md = "![](image.jpg)"
    gem = "=> image.jpg"
    assert normalize(md2gemini(md, img_tag="")) == gem


def test_empty_img_tag_with_text():
    md = "![text](image.jpg)"
    gem = "=> image.jpg text"
    assert normalize(md2gemini(md, img_tag="")) == gem


@multiple_tags
def table_tag(request):
    md = """
a|b|c
-|-|
1|2|3
4|5|6
""".lstrip()
    gem = (
        "```"
        + request.param
        + """
┌───┬───┬───┐
│ a │ b │ c │
╞═══╪═══╪═══╡
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
└───┴───┴───┘
```"""
    )
    assert normalize(md2gemini(md, table_tag=request.param)) == gem


def test_table_tag(table_tag):
    pass
