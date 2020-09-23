from .util import normalize
from md2gemini import md2gemini
import pytest


def f(md):
    return normalize(md2gemini(md))


def test_normal_list():
    md = "- hi\n- oh"
    gem = "* hi\n* oh"
    assert f(md) == gem


@pytest.fixture(params=[2, 3, 4, 5, 6])
def list_with_newline_and_spaces(request):
    md = "- hello\n" + (" " * request.param) + "world\n- oh"
    gem = "* hello world\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_spaces(list_with_newline_and_spaces):
    pass


def test_separate_lists():
    md = "* hello\n\n- oh"
    gem = "* hello\n\n* oh"
    assert f(md) == gem
