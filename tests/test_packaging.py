import importlib
from unittest.mock import MagicMock, patch

import mark2tex


def test_package_importable():
    assert importlib.import_module("mark2tex") is not None

def test_version_defined():
    assert hasattr(mark2tex, "__version__")

def test_main_module_importable():
    assert importlib.import_module("mark2tex.__main__") is not None


def test_main_runs_app() -> None:
    with patch("mark2tex.main.Mark2TeXApp") as mock_app_class:
        mock_instance = MagicMock()
        mock_app_class.return_value = mock_instance

        from mark2tex.main import main
        main()

        mock_app_class.assert_called_once()
        mock_instance.run.assert_called_once()
