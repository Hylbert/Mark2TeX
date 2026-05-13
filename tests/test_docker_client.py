"""Unit tests for mark2tex.docker_client.get_docker_client.

All tests are pure unit tests — no real Docker daemon is required.
Each test mocks at the correct layer so the CI environment does not
need Docker installed.
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from docker.errors import DockerException

import mark2tex.docker_client as dc
from mark2tex.docker_client import get_docker_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_client() -> MagicMock:
    """Return a MagicMock that looks like a connected DockerClient."""
    client = MagicMock()
    client.ping.return_value = True
    return client


# ---------------------------------------------------------------------------
# Linux / other platforms — delegates to docker.from_env()
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_client.platform.system", return_value="Linux")
@patch("mark2tex.docker_client.docker.from_env")
def test_linux_delegates_to_from_env(mock_from_env, _mock_system):
    expected = _mock_client()
    mock_from_env.return_value = expected

    result = get_docker_client()

    mock_from_env.assert_called_once()
    assert result is expected


@patch("mark2tex.docker_client.platform.system", return_value="FreeBSD")
@patch("mark2tex.docker_client.docker.from_env")
def test_other_platform_delegates_to_from_env(mock_from_env, _mock_system):
    expected = _mock_client()
    mock_from_env.return_value = expected

    result = get_docker_client()

    mock_from_env.assert_called_once()
    assert result is expected


# ---------------------------------------------------------------------------
# macOS — DOCKER_HOST set: skip probe, use from_env()
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_client.platform.system", return_value="Darwin")
@patch("mark2tex.docker_client.docker.from_env")
def test_macos_docker_host_env_skips_probe(mock_from_env, _mock_system, monkeypatch):
    monkeypatch.setenv("DOCKER_HOST", "unix:///custom/docker.sock")
    expected = _mock_client()
    mock_from_env.return_value = expected

    result = get_docker_client()

    mock_from_env.assert_called_once()
    assert result is expected


# ---------------------------------------------------------------------------
# macOS — probe: first existing + pingable socket wins
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_client.platform.system", return_value="Darwin")
@patch("mark2tex.docker_client.docker.DockerClient")
@patch("mark2tex.docker_client.Path.exists")
def test_macos_returns_first_reachable_socket(mock_exists, mock_docker_client, _mock_system, monkeypatch):
    monkeypatch.delenv("DOCKER_HOST", raising=False)

    # Only the first candidate exists and pings successfully.
    mock_exists.return_value = True
    expected = _mock_client()
    mock_docker_client.return_value = expected

    result = get_docker_client()

    first_candidate = dc._MACOS_SOCKET_CANDIDATES[0]
    mock_docker_client.assert_called_once_with(base_url=f"unix://{first_candidate}")
    expected.ping.assert_called_once()
    assert result is expected


@patch("mark2tex.docker_client.platform.system", return_value="Darwin")
@patch("mark2tex.docker_client.docker.DockerClient")
@patch("mark2tex.docker_client.Path.exists")
def test_macos_skips_socket_when_ping_fails(mock_exists, mock_docker_client, _mock_system, monkeypatch):
    """Socket file exists but daemon is not running — ping() raises → try next."""
    monkeypatch.delenv("DOCKER_HOST", raising=False)

    # All candidates exist, but only the second one pings.
    mock_exists.return_value = True
    dead_client = MagicMock()
    dead_client.ping.side_effect = DockerException("daemon not running")
    live_client = _mock_client()
    mock_docker_client.side_effect = [dead_client, live_client]

    result = get_docker_client()

    assert result is live_client
    assert mock_docker_client.call_count == 2


@patch("mark2tex.docker_client.platform.system", return_value="Darwin")
@patch("mark2tex.docker_client.docker.DockerClient")
@patch("mark2tex.docker_client.Path.exists", return_value=False)
def test_macos_raises_when_no_candidate_works(mock_exists, mock_docker_client, _mock_system, monkeypatch):
    """No socket file exists at all — must raise DockerException."""
    monkeypatch.delenv("DOCKER_HOST", raising=False)

    with pytest.raises(DockerException) as exc_info:
        get_docker_client()

    assert "DOCKER_HOST" in str(exc_info.value)
    mock_docker_client.assert_not_called()


@patch("mark2tex.docker_client.platform.system", return_value="Darwin")
@patch("mark2tex.docker_client.docker.DockerClient")
@patch("mark2tex.docker_client.Path.exists", return_value=True)
def test_macos_raises_when_all_pings_fail(mock_exists, mock_docker_client, _mock_system, monkeypatch):
    """All socket files exist but every daemon is unreachable — must raise."""
    monkeypatch.delenv("DOCKER_HOST", raising=False)

    dead_client = MagicMock()
    dead_client.ping.side_effect = DockerException("not running")
    mock_docker_client.return_value = dead_client

    with pytest.raises(DockerException) as exc_info:
        get_docker_client()

    assert "DOCKER_HOST" in str(exc_info.value)
    assert mock_docker_client.call_count == len(dc._MACOS_SOCKET_CANDIDATES)


# ---------------------------------------------------------------------------
# Windows — success and failure paths
# ---------------------------------------------------------------------------

@patch("mark2tex.docker_client.platform.system", return_value="Windows")
@patch("mark2tex.docker_client.docker.from_env")
def test_windows_returns_client_on_success(mock_from_env, _mock_system):
    expected = _mock_client()
    mock_from_env.return_value = expected

    result = get_docker_client()

    mock_from_env.assert_called_once()
    assert result is expected


@patch("mark2tex.docker_client.platform.system", return_value="Windows")
@patch("mark2tex.docker_client.docker.from_env", side_effect=DockerException("pipe not found"))
def test_windows_rewrites_exception_message(mock_from_env, _mock_system):
    with pytest.raises(DockerException) as exc_info:
        get_docker_client()

    msg = str(exc_info.value)
    assert "Docker Desktop" in msg or "Rancher Desktop" in msg or "Podman Desktop" in msg


@patch("mark2tex.docker_client.platform.system", return_value="Windows")
@patch("mark2tex.docker_client.docker.from_env", side_effect=DockerException("pipe not found"))
def test_windows_exception_chains_original(mock_from_env, _mock_system):
    """The re-raised exception must chain the original via __cause__."""
    with pytest.raises(DockerException) as exc_info:
        get_docker_client()

    assert exc_info.value.__cause__ is not None
    assert "pipe not found" in str(exc_info.value.__cause__)
