import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mark2tex.docker_manager import DockerManager


@pytest.fixture
def manager():
    return DockerManager()


def test_list_templates_returns_list(manager, tmp_path, monkeypatch):
    (tmp_path / "artigo-abnt").mkdir()
    (tmp_path / "artigo-abnt" / "template.tex").touch()
    (tmp_path / "tcc-abnt").mkdir()
    (tmp_path / "tcc-abnt" / "template.tex").touch()
    monkeypatch.setattr(manager, "templates_dir", tmp_path)
    result = manager.list_templates()
    assert isinstance(result, list)
    assert "artigo-abnt" in result
    assert "tcc-abnt" in result


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_missing_file(mock_popen, manager, tmp_path):
    mock_process = MagicMock()
    mock_process.stdout = iter([])
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    results = list(manager.compile("nonexistent.md", "artigo-abnt"))
    assert any("not found" in r or "Error" in r for r in results)


def test_list_templates_empty_if_no_dir(manager, tmp_path, monkeypatch):
    monkeypatch.setattr(manager, "templates_dir", tmp_path / "nonexistent")
    result = manager.list_templates()
    assert result == []


@patch("mark2tex.docker_manager.docker.from_env")
def test_uninstall_docker_assets_image_not_found(mock_docker, capsys):
    from mark2tex.docker_manager import uninstall_docker_assets
    from docker.errors import ImageNotFound
    mock_client = MagicMock()
    mock_docker.return_value = mock_client
    mock_client.images.get.side_effect = ImageNotFound("mark2tex:latest")
    uninstall_docker_assets()
    captured = capsys.readouterr()
    assert "n\u00e3o encontrada" in captured.out
