from .util import normalize
from md2gemini import md2gemini


def f(md):
    return normalize(md2gemini(md))


def test_normal_list():
    md = "- hi\n- oh"
    gem = "* hi\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_no_space():
    md = "- hello\nworld\n- oh"
    gem = "* hello world\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_one_space():
    md = "- hello\n world\n- oh"
    gem = "* hello world\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_two_spaces():
    md = "- hello\n  world\n- oh"
    gem = "* hello world\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_three_spaces():
    md = "- hello\n   bright\n   world\n- oh"
    gem = "* hello bright world\n* oh"
    assert f(md) == gem


def test_list_with_newline_and_four_spaces():
    md = "- hello\n    world\n- oh"
    gem = "* hello world\n* oh"
    assert f(md) == gem


def test_separate_lists():
    md = "* hello\n\n- oh"
    gem = "* hello\n\n* oh"
    assert f(md) == gem
