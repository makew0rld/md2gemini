from .util import normalize
from md2gemini import md2gemini
import pytest

multiple_tags = pytest.fixture(params=["[IMG]", "IMG", "test", "AAA"])

@multiple_tags
def tag_no_text(request):
    md = "![](image.jpg)"
    gem = "=> image.jpg " + request.param
    assert normalize(md2gemini(md, img_tag=request.param)) == gem

def test_tag_no_text(tag_no_text):
    pass

@multiple_tags
def tag_with_text(request):
    md = "![text](image.jpg)"
    gem = "=> image.jpg text " + request.param
    assert normalize(md2gemini(md, img_tag=request.param)) == gem

def test_tag_with_text(tag_with_text):
    pass

def test_empty_tag_no_text():
    md = "![](image.jpg)"
    gem = "=> image.jpg"
    assert normalize(md2gemini(md, img_tag="")) == gem

def test_empty_tag_with_text():
    md = "![text](image.jpg)"
    gem = "=> image.jpg text"
    assert normalize(md2gemini(md, img_tag="")) == gem