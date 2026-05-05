import importlib

import mark2tex


def test_mark2tex_importable():
    assert importlib.import_module("mark2tex") is not None


def test_has_version():
    assert hasattr(mark2tex, "__version__")


def test_main_module_importable():
    assert importlib.import_module("mark2tex.__main__") is not None


def test_main_function_callable():
    from unittest.mock import patch
    with patch("mark2tex.main.Mark2TeXApp") as mock_app_class:
        mock_app = mock_app_class.return_value
        mock_app.run.return_value = None
        from mark2tex.main import main
        main()
        mock_app.run.assert_called_once()
