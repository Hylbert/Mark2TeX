"""Tests for DockerManager — compatible with the queue-based streaming compile().

The new compile() implementation reads stdout line-by-line via a background
thread + queue.Queue instead of calling communicate(). Mocks must therefore
provide a realistic stdout object whose readline() method yields lines and
then returns "" to signal EOF.
"""
import io
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from mark2tex.docker_manager import DockerManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_popen_mock(lines: list[str], returncode: int = 0) -> MagicMock:
    """Build a Popen mock whose stdout streams *lines* then EOF.

    readline() is implemented via an iterator over *lines* followed by
    an infinite stream of "" so the reader thread terminates cleanly.
    """
    mock_proc = MagicMock()
    mock_proc.returncode = returncode
    mock_proc.poll.return_value = returncode  # process already finished
    mock_proc.wait.return_value = returncode

    # Build a StringIO-like object that readline() can iterate.
    content = "".join(lines)
    mock_proc.stdout = io.StringIO(content)

    return mock_proc


# ---------------------------------------------------------------------------
# Basic instantiation
# ---------------------------------------------------------------------------

def test_manager_instantiates():
    dm = DockerManager()
    assert dm is not None


def test_bin_dir_is_set():
    dm = DockerManager()
    assert isinstance(dm.bin_dir, Path)


def test_templates_dir_is_set():
    dm = DockerManager()
    assert isinstance(dm.templates_dir, Path)


# ---------------------------------------------------------------------------
# compile() — missing file
# ---------------------------------------------------------------------------

def test_compile_missing_file_yields_error():
    dm = DockerManager()
    result = list(dm.compile("arquivo_que_nao_existe.md", "tcc-abnt"))
    assert any("\u274c" in line for line in result)


# ---------------------------------------------------------------------------
# compile() — command construction
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_builds_correct_command(mock_popen):
    mock_proc = _make_popen_mock(["PROGRESS:50%\n"])
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        os.unlink(tmpfile)

    assert mock_popen.called
    cmd = mock_popen.call_args[0][0]
    assert "docker" in cmd
    assert "run" in cmd
    assert "mark2tex:latest" in cmd


# ---------------------------------------------------------------------------
# compile() — success: all stdout lines are yielded
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_success_yields_stdout_lines(mock_popen):
    lines = ["line one\n", "line two\n", "line three\n"]
    mock_proc = _make_popen_mock(lines, returncode=0)
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        result = list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        os.unlink(tmpfile)

    assert "line one\n" in result
    assert "line two\n" in result
    assert "line three\n" in result


# ---------------------------------------------------------------------------
# compile() — non-zero exit code yields error line
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_docker_process_error(mock_popen):
    mock_proc = _make_popen_mock(["Error in build process\n"], returncode=1)
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        result = list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        os.unlink(tmpfile)

    assert any("\u274c Error: Docker process exited with code 1" in line for line in result)


# ---------------------------------------------------------------------------
# compile() — timeout: deadline expires when no lines arrive
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.COMPILE_TIMEOUT", 2)
@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_yields_error_message(mock_popen):
    """When no lines arrive within COMPILE_TIMEOUT seconds, a \u274c timeout line is yielded."""
    import threading

    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.poll.return_value = None
    mock_proc.wait.return_value = None

    # stdout.readline blocks for 5 s then returns "" — longer than the 2 s timeout.
    done = threading.Event()

    def slow_readline():
        done.wait(timeout=5)
        return ""

    mock_proc.stdout.readline = slow_readline
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        result = list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        done.set()  # unblock the reader thread
        os.unlink(tmpfile)

    assert len(result) == 1
    assert "\u274c" in result[0]
    assert "Timeout" in result[0] or "timeout" in result[0]


@patch("mark2tex.docker_manager.COMPILE_TIMEOUT", 2)
@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_kills_process(mock_popen):
    """process.kill() must be called when the deadline expires."""
    import threading

    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.poll.return_value = None
    mock_proc.wait.return_value = None
    done = threading.Event()

    def slow_readline():
        done.wait(timeout=5)
        return ""

    mock_proc.stdout.readline = slow_readline
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        done.set()
        os.unlink(tmpfile)

    mock_proc.kill.assert_called()


@patch("mark2tex.docker_manager.COMPILE_TIMEOUT", 2)
@patch("mark2tex.docker_manager.subprocess.Popen")
def test_compile_timeout_message_contains_timeout_value(mock_popen):
    """The timeout error message must include the timeout duration."""
    import threading

    mock_proc = MagicMock()
    mock_proc.returncode = None
    mock_proc.poll.return_value = None
    mock_proc.wait.return_value = None
    done = threading.Event()

    def slow_readline():
        done.wait(timeout=5)
        return ""

    mock_proc.stdout.readline = slow_readline
    mock_popen.return_value = mock_proc

    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        f.write(b"# Test")
        tmpfile = f.name

    try:
        dm = DockerManager()
        result = list(dm.compile(tmpfile, "tcc-abnt"))
    finally:
        done.set()
        os.unlink(tmpfile)

    assert "2" in result[0]  # COMPILE_TIMEOUT patched to 2


# ---------------------------------------------------------------------------
# COMPILE_TIMEOUT env var
# ---------------------------------------------------------------------------

def test_compile_timeout_env_var_sets_constant():
    """MARK2TEX_TIMEOUT env var must be read at import time to set COMPILE_TIMEOUT."""
    import importlib

    import mark2tex.docker_manager as dm_mod

    with patch.dict(os.environ, {"MARK2TEX_TIMEOUT": "120"}):
        importlib.reload(dm_mod)
        assert dm_mod.COMPILE_TIMEOUT == 120

    # Restore default
    importlib.reload(dm_mod)


# ---------------------------------------------------------------------------
# uninstall helpers
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_manager.docker.from_env")
def test_uninstall_when_image_not_found(mock_docker):
    from docker.errors import ImageNotFound

    from mark2tex.docker_manager import uninstall_docker_assets

    mock_client = MagicMock()
    mock_client.images.get.side_effect = ImageNotFound("not found")
    mock_docker.return_value = mock_client
    uninstall_docker_assets()  # Should not raise


@patch("mark2tex.docker_manager.docker.from_env")
def test_uninstall_docker_exception(mock_docker):
    from docker.errors import DockerException

    from mark2tex.docker_manager import uninstall_docker_assets

    mock_client = MagicMock()
    mock_client.images.get.side_effect = DockerException("Connection error")
    mock_docker.return_value = mock_client
    uninstall_docker_assets()  # Should not raise


# ---------------------------------------------------------------------------
# Removed tests (kept as documentation of the old communicate() contract)
# ---------------------------------------------------------------------------
# test_compile_timeout_drains_pipe  — no longer applicable; communicate() gone.
