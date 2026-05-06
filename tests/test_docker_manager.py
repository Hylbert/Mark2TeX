import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from mark2tex.docker_manager import DockerManager


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


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_builds_correct_command(mock_popen):
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = ("PROGRESS:50%\n", None)
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


@patch("mark2tex.docker_manager.docker.from_env")
def test_uninstall_when_image_not_found(mock_docker):
    from docker.errors import ImageNotFound

    from mark2tex.docker_manager import uninstall_docker_assets

    mock_client = MagicMock()
    mock_client.images.get.side_effect = ImageNotFound("not found")
    mock_docker.return_value = mock_client
    uninstall_docker_assets()  # Should not raise


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_docker_process_error(mock_popen):
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = ("Error in build process\n", None)
    mock_proc.returncode = 1
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        result = list(dm.compile(tmpfile, "tcc-abnt"))

    assert any("\u274c Error: Docker process exited with code 1" in line for line in result)
    os.unlink(tmpfile)


@patch("mark2tex.docker_manager.docker.from_env")
def test_uninstall_docker_exception(mock_docker):
    from docker.errors import DockerException

    from mark2tex.docker_manager import uninstall_docker_assets
    mock_client = MagicMock()
    mock_client.images.get.side_effect = DockerException("Connection error")
    mock_docker.return_value = mock_client
    uninstall_docker_assets()  # Should not raise


# ---------------------------------------------------------------------------
# Timeout tests  (new behaviour)
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_yields_error_message(mock_popen):
    """When communicate() raises TimeoutExpired, compile yields a ❌ timeout line."""
    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd="docker", timeout=300),
        ("" , None),  # second call after kill() to drain the pipe
    ]
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        result = list(dm.compile(tmpfile, "tcc-abnt"))

    assert len(result) == 1
    assert "\u274c" in result[0]
    assert "Timeout" in result[0] or "timeout" in result[0]
    os.unlink(tmpfile)


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_kills_process(mock_popen):
    """process.kill() must be called when TimeoutExpired is raised."""
    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd="docker", timeout=300),
        ("", None),
    ]
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        list(dm.compile(tmpfile, "tcc-abnt"))

    mock_proc.kill.assert_called_once()
    os.unlink(tmpfile)


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_drains_pipe(mock_popen):
    """communicate() must be called a second time after kill() to drain the pipe."""
    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd="docker", timeout=300),
        ("", None),
    ]
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        list(dm.compile(tmpfile, "tcc-abnt"))

    assert mock_proc.communicate.call_count == 2
    os.unlink(tmpfile)


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_success_yields_stdout_lines(mock_popen):
    """On success, every non-empty stdout line is yielded."""
    stdout = "line one\nline two\nline three\n"
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = (stdout, None)
    mock_proc.returncode = 0
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        result = list(dm.compile(tmpfile, "tcc-abnt"))

    assert "line one\n" in result
    assert "line two\n" in result
    assert "line three\n" in result
    os.unlink(tmpfile)


@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_message_contains_timeout_value(mock_popen):
    """The timeout error message must include the timeout duration."""
    mock_proc = MagicMock()
    mock_proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd="docker", timeout=300),
        ("", None),
    ]
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    dm = DockerManager()
    with patch.object(Path, "exists", return_value=True):
        result = list(dm.compile(tmpfile, "tcc-abnt"))

    assert "300" in result[0]
    os.unlink(tmpfile)


def test_compile_timeout_env_var_sets_constant():
    """MARK2TEX_TIMEOUT env var must be read at import time to set COMPILE_TIMEOUT."""
    import importlib

    import mark2tex.docker_manager as dm_mod

    with patch.dict(os.environ, {"MARK2TEX_TIMEOUT": "120"}):
        importlib.reload(dm_mod)
        assert dm_mod.COMPILE_TIMEOUT == 120

    # Restore default
    importlib.reload(dm_mod)
