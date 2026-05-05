from mark2tex.log_translator import log_translator


def test_log_translator_returns_string():
    result = log_translator("Some LaTeX log output")
    assert isinstance(result, str)


def test_log_translator_handles_empty():
    result = log_translator("")
    assert isinstance(result, str)


def test_log_translator_handles_error_line():
    line = "! Undefined control sequence."
    result = log_translator(line)
    assert isinstance(result, str)
    assert len(result) > 0
