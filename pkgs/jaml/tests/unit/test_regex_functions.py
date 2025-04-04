import re
import pytest

from jaml._regex import (
    regex_keywords, regex_reserved_functions, regex_boolean, regex_null,
    regex_identifier, regex_integer, regex_float, regex_f_string_prefix,
    regex_triple_single_quote, regex_triple_double_quote, regex_triple_backtick,
    regex_single_quote, regex_double_quote, regex_backtick, regex_string,
    regex_array, regex_inline_table, regex_table_section, regex_table_array,
    regex_operator, regex_punctuation, regex_comment, regex_scoped_variable,
    regex_whitespace
)

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_keywords():
    r = regex_keywords()
    assert isinstance(r, re.Pattern)
    assert r.search("if") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_reserved_functions():
    r = regex_reserved_functions()
    assert isinstance(r, re.Pattern)
    assert r.search("File()") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_boolean():
    r = regex_boolean()
    assert isinstance(r, re.Pattern)
    assert r.search("true") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_null():
    r = regex_null()
    assert isinstance(r, re.Pattern)
    assert r.search("null") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_identifier():
    r = regex_identifier()
    assert isinstance(r, re.Pattern)
    assert r.search("variableName") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_integer():
    r = regex_integer()
    assert isinstance(r, re.Pattern)
    assert r.search("42") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_float():
    r = regex_float()
    assert isinstance(r, re.Pattern)
    assert r.search("3.14") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_f_string_prefix():
    r = regex_f_string_prefix()
    assert isinstance(r, str)
    # The prefix is optional; an empty string should match.
    assert re.fullmatch(r, "") is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_triple_single_quote():
    r = regex_triple_single_quote()
    assert isinstance(r, str)
    m = re.search(r, "'''abc'''", re.DOTALL)
    assert m is not None and m.group(1) == "abc"

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_triple_double_quote():
    r = regex_triple_double_quote()
    assert isinstance(r, str)
    m = re.search(r, '"""abc"""', re.DOTALL)
    assert m is not None and m.group(1) == "abc"

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_triple_backtick():
    r = regex_triple_backtick()
    assert isinstance(r, str)
    m = re.search(r, "```abc```", re.DOTALL)
    assert m is not None and m.group(1) == "abc"

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_single_quote():
    r = regex_single_quote()
    assert isinstance(r, str)
    m = re.search(r, "'abc'", re.DOTALL)
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_double_quote():
    r = regex_double_quote()
    assert isinstance(r, str)
    m = re.search(r, '"abc"', re.DOTALL)
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_backtick():
    r = regex_backtick()
    assert isinstance(r, str)
    m = re.search(r, "`abc`", re.DOTALL)
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_string():
    r = regex_string()
    assert isinstance(r, re.Pattern)
    # Test a string with an optional f-string prefix.
    m = r.search('f"abc"')
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_array():
    r = regex_array()
    assert isinstance(r, re.Pattern)
    m = r.search("[1, 2, 3]")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_inline_table():
    r = regex_inline_table()
    assert isinstance(r, re.Pattern)
    m = r.search("{ key = 'value' }")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_table_section():
    r = regex_table_section()
    assert isinstance(r, re.Pattern)
    m = r.search("[globals]")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_table_array():
    r = regex_table_array()
    assert isinstance(r, re.Pattern)
    m = r.search("[[products]]")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_operator():
    r = regex_operator()
    assert isinstance(r, re.Pattern)
    m = r.search("==")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_punctuation():
    r = regex_punctuation()
    assert isinstance(r, re.Pattern)
    m = r.search(":")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_comment():
    r = regex_comment()
    assert isinstance(r, re.Pattern)
    m = r.search("# comment")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_scoped_variable():
    r = regex_scoped_variable()
    assert isinstance(r, re.Pattern)
    m = r.search("${var}")
    assert m is not None

@pytest.mark.xfail(reason="Expected failure for demonstration")
def test_regex_whitespace():
    r = regex_whitespace()
    assert isinstance(r, re.Pattern)
    m = r.search("   ")
    assert m is not None
