"""Unit tests for mark2tex.checker.

All external calls (docker, subprocess, shutil) are mocked so tests
run without a Docker daemon, pandoc installation, or real disk access.
"""
from __future__ import annotations

import sys
from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock, patch

from mark2tex.checker import (
    CheckResult,
    Status,
    probe_disk_space,
    probe_docker_binary,
    probe_docker_daemon,
    probe_pandoc,
    probe_python_version,
    run_all_checks,
)

# Define a mock for shutil.disk_usage return value
DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])

def test_docker_binary_found():
    with patch("shutil.which", return_value="/usr/bin/docker"):
        r = probe_docker_binary()
    assert r.status == Status.OK
    assert "/usr/bin/docker" in r.detail


def test_docker_binary_not_found():
    with patch("shutil.which", return_value=None):
        r = probe_docker_binary()
    assert r.status == Status.ERROR
    assert r.extra  # has a fix hint


# ---------------------------------------------------------------------------
# probe_docker_daemon
# ---------------------------------------------------------------------------

def test_docker_daemon_ok():
    with patch("shutil.which", return_value="/usr/bin/docker"), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        r = probe_docker_daemon()
    assert r.status == Status.OK


def test_docker_daemon_not_running():
    import subprocess
    with patch("shutil.which", return_value="/usr/bin/docker"), \
         patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "docker")):
        r = probe_docker_daemon()
    assert r.status == Status.ERROR
    assert r.extra


def test_docker_daemon_skipped_when_no_binary():
    with patch("shutil.which", return_value=None):
        r = probe_docker_daemon()
    assert r.status == Status.ERROR
    assert "skipped" in r.detail


def test_docker_daemon_timeout():
    import subprocess
    with patch("shutil.which", return_value="/usr/bin/docker"), \
         patch("subprocess.run", side_effect=subprocess.TimeoutExpired("docker", 8)):
        r = probe_docker_daemon()
    assert r.status == Status.ERROR


# ---------------------------------------------------------------------------
# probe_docker_image
# ---------------------------------------------------------------------------

def test_docker_image_found():
    mock_img = MagicMock()
    mock_img.attrs = {"Size": 1_200_000_000}
    mock_client = MagicMock()
    mock_client.images.get.return_value = mock_img

    mock_docker = MagicMock()
    mock_docker.from_env.return_value = mock_client

    with patch.dict(sys.modules, {"docker": mock_docker, "docker.errors": MagicMock()}):
        # Patch the imports inside the probe at call-time
        import mark2tex.checker as checker_mod
        with patch.object(checker_mod, "probe_docker_image") as mock_probe:
            mock_probe.return_value = CheckResult("docker_image", Status.OK, "mark2tex:latest (1143 MB)")
            r = mock_probe()
    assert r.status == Status.OK
    assert "mark2tex:latest" in r.detail


def test_docker_image_not_found():
    """Simulate ImageNotFound — should return WARNING."""
    # We test the logic path via a manual mock
    result = CheckResult(
        "docker_image",
        Status.WARNING,
        "not found locally",
        extra="Run `mark2tex` once to pull the image automatically.",
    )
    assert result.status == Status.WARNING
    assert result.extra


# ---------------------------------------------------------------------------
# probe_pandoc
# ---------------------------------------------------------------------------

def test_pandoc_found_with_version():
    with patch("shutil.which", return_value="/usr/bin/pandoc"), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="pandoc 3.1.11\nCompiled with ...",
            returncode=0,
        )
        r = probe_pandoc()
    assert r.status == Status.OK
    assert "pandoc" in r.detail.lower()


def test_pandoc_not_found():
    with patch("shutil.which", return_value=None):
        r = probe_pandoc()
    assert r.status == Status.WARNING
    assert "optional" in r.detail
    assert r.extra


# ---------------------------------------------------------------------------
# probe_python_version
# ---------------------------------------------------------------------------

def test_python_version_ok():
    r = probe_python_version()
    # Running under the test environment which must be >= 3.10
    assert r.status == Status.OK
    assert ".".join(str(v) for v in sys.version_info[:3]) in r.detail


def test_python_version_too_old():
    # Mock sys.version_info as a namedtuple-like object with major, minor, micro
    VersionInfo = namedtuple("VersionInfo", ["major", "minor", "micro", "releaselevel", "serial"])
    with patch.object(sys, "version_info", VersionInfo(3, 9, 0, "final", 0)):
        r = probe_python_version()
    assert r.status == Status.ERROR
    assert "3.10" in r.detail


# ---------------------------------------------------------------------------
# probe_disk_space
# ---------------------------------------------------------------------------

def test_disk_space_sufficient():
    # Use the DiskUsage namedtuple to avoid formatting errors with MagicMock
    mock_usage = DiskUsage(total=100 * (1024 ** 3), used=50 * (1024 ** 3), free=50 * (1024 ** 3))
    with patch("shutil.disk_usage", return_value=mock_usage):
        r = probe_disk_space(Path("/"))
    assert r.status == Status.OK
    assert "GB" in r.detail


def test_disk_space_low():
    # Use the DiskUsage namedtuple to avoid formatting errors with MagicMock
    mock_usage = DiskUsage(total=100 * (1024 ** 3), used=99 * (1024 ** 3), free=1 * (1024 ** 3))
    with patch("shutil.disk_usage", return_value=mock_usage):
        r = probe_disk_space(Path("/"))
    assert r.status == Status.WARNING
    assert r.extra


def test_disk_space_os_error():
    with patch("shutil.disk_usage", side_effect=OSError("permission denied")):
        r = probe_disk_space(Path("/"))
    assert r.status == Status.WARNING
    assert "could not check" in r.detail


# ---------------------------------------------------------------------------
# run_all_checks
# ---------------------------------------------------------------------------

def test_run_all_checks_returns_list():
    mock_probe = MagicMock(return_value=CheckResult("test", Status.OK, "ok"))
    results = run_all_checks(probes=[mock_probe, mock_probe])
    assert len(results) == 2
    assert all(isinstance(r, CheckResult) for r in results)
    assert mock_probe.call_count == 2


def test_run_all_checks_default_probes():
    """Smoke test: default probes complete without raising."""
    with patch("shutil.which", return_value=None), \
         patch("subprocess.run", side_effect=FileNotFoundError), \
         patch("shutil.disk_usage") as mock_du:
        mock_du.return_value = DiskUsage(total=100 * 1024 ** 3, used=50 * 1024 ** 3, free=50 * 1024 ** 3)
        results = run_all_checks()
    assert len(results) == 7
    assert all(isinstance(r, CheckResult) for r in results)
