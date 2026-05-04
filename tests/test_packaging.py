import importlib
import src
from unittest.mock import patch, MagicMock

def test_package_importable():
    assert importlib.import_module("src") is not None

def test_version_defined():
    assert hasattr(src, "__version__")

def test_main_module_importable():
    assert importlib.import_module("src.__main__") is not None


def test_main_runs_app() -> None:
    with patch("src.main.Mark2TeXApp") as mock_app_class:
        mock_instance = MagicMock()
        mock_app_class.return_value = mock_instance

        from src.main import main
        main()

        mock_app_class.assert_called_once()
        mock_instance.run.assert_called_once()
