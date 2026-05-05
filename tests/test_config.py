import json
from pathlib import Path
from unittest.mock import patch

from mark2tex.config import DEFAULTS, load, save


def test_load_defaults_when_no_file():
    """Ensure defaults are returned when no config file exists."""
    with patch.object(Path, "exists", return_value=False):
        assert load() == DEFAULTS

def test_load_merges_with_defaults():
    """Ensure user settings override and merge with defaults."""
    user_settings = {"theme": "custom-theme"}
    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "read_text", return_value=json.dumps(user_settings)):
            config = load()
            assert config["theme"] == "custom-theme"
            assert config["language"] == DEFAULTS["language"]

def test_load_fallback_on_corrupted_json():
    """Ensure fallback to defaults when config file contains invalid JSON."""
    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "read_text", return_value="invalid json {"):
            assert load() == DEFAULTS

def test_load_fallback_on_os_error():
    """Ensure fallback to defaults when a filesystem error occurs."""
    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
            assert load() == DEFAULTS

def test_save_writes_correctly(tmp_path):
    """Verify that settings are correctly written to the config file."""
    # Mock CONFIG_FILE to use a temporary directory
    test_config_file = tmp_path / "config.json"

    with patch("mark2tex.config.CONFIG_FILE", test_config_file), \
         patch("mark2tex.config.CONFIG_DIR", tmp_path):

        settings = {"language": "en_US", "theme": "light"}
        save(settings)

        assert test_config_file.exists()
        loaded_data = json.loads(test_config_file.read_text(encoding="utf-8"))
        assert loaded_data == settings
