import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.docker_manager import DockerManager


def test_manager_instantiates():
    dm = DockerManager()
    assert dm is not None


def test_bin_dir_is_set():
    dm = DockerManager()
    assert isinstance(dm.bin_dir, Path)


def test_templates_dir_is_set():
    dm = DockerManager()
    assert isinstance(dm.templates_dir, Path)


def test_compile_missing_file_yields_error():
    dm = DockerManager()
    result = list(dm.compile("arquivo_que_nao_existe.md", "tcc-abnt"))
    assert any("\u274c" in line for line in result)


@patch("src.docker_manager.subprocess.Popen")
def test_compile_builds_correct_command(mock_popen):
    mock_proc = MagicMock()
    mock_proc.stdout = iter(["PROGRESS:50%\n"])
    mock_proc.returncode = 0
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        list(dm.compile(tmpfile, "tcc-abnt"))

    assert mock_popen.called
    cmd = mock_popen.call_args[0][0]
    assert "docker" in cmd
    assert "run" in cmd
    assert "mark2tex:latest" in cmd

    os.unlink(tmpfile)


@patch("src.docker_manager.docker.from_env")
def test_uninstall_when_image_not_found(mock_docker):
    from docker.errors import ImageNotFound

    from src.docker_manager import uninstall_docker_assets

    mock_client = MagicMock()
    mock_client.images.get.side_effect = ImageNotFound("not found")
    mock_docker.return_value = mock_client
    uninstall_docker_assets()  # Should not raise
