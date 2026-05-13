"""Shared Docker client factory for Mark2TeX.

Provides ``get_docker_client()`` — a cross-platform replacement for the
bare ``docker.from_env()`` call that fails on macOS when Docker Desktop
or Colima places the socket at a non-standard path.

Platform behaviour
------------------
Linux
    Falls through to ``docker.from_env()``, which reads DOCKER_HOST or
    defaults to ``/var/run/docker.sock``. No change in behaviour.

macOS
    Probes the following socket paths in order:

    1. ``~/.docker/run/docker.sock``  — Docker Desktop
    2. ``~/.colima/default/docker.sock`` — Colima
    3. ``~/.lima/docker/sock/docker.sock`` — Lima / nerdctl
    4. ``/var/run/docker.sock`` — legacy / Docker Engine via brew

    If ``DOCKER_HOST`` is already set in the environment the probe loop
    is skipped and ``docker.from_env()`` is used as-is, so power users
    who set the variable manually are not affected.

Windows
    Wraps ``docker.from_env()`` and rewrites the ``DockerException`` into
    a friendlier message that mentions Docker Desktop, Rancher Desktop and
    Podman Desktop — the most common Windows runtimes.
"""
from __future__ import annotations

import os
import platform
from pathlib import Path

import docker
from docker.errors import DockerException

# Ordered list of candidate socket paths probed on macOS when DOCKER_HOST
# is not explicitly set by the user.
_MACOS_SOCKET_CANDIDATES: tuple[str, ...] = (
    os.path.expanduser("~/.docker/run/docker.sock"),      # Docker Desktop
    os.path.expanduser("~/.colima/default/docker.sock"),  # Colima
    os.path.expanduser("~/.lima/docker/sock/docker.sock"),  # Lima
    "/var/run/docker.sock",  # Docker Engine / legacy
)


def get_docker_client() -> docker.DockerClient:
    """Return a connected DockerClient, detecting the right socket automatically.

    Raises
    ------
    DockerException
        If no reachable Docker socket / daemon is found on the current
        platform.  The exception message is human-readable and actionable.
    """
    system = platform.system()

    # ── macOS ────────────────────────────────────────────────────────────────
    if system == "Darwin":
        # If the user already set DOCKER_HOST, respect it unconditionally.
        if os.environ.get("DOCKER_HOST"):
            return docker.from_env()

        for sock in _MACOS_SOCKET_CANDIDATES:
            if Path(sock).exists():
                try:
                    client = docker.DockerClient(base_url=f"unix://{sock}")
                    # Ping the daemon to confirm it is actually responding.
                    client.ping()
                    return client
                except DockerException:
                    continue  # socket file exists but daemon is not running

        raise DockerException(
            "Docker socket not found on macOS.\n"
            "Make sure Docker Desktop or Colima is running, or set:\n"
            "  export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock"
        )

    # ── Windows ──────────────────────────────────────────────────────────────
    if system == "Windows":
        try:
            return docker.from_env()
        except DockerException as exc:
            raise DockerException(
                "Could not connect to Docker on Windows.\n"
                "Make sure one of the following is installed and running:\n"
                "  \u2022 Docker Desktop  https://www.docker.com/products/docker-desktop\n"
                "  \u2022 Rancher Desktop https://rancherdesktop.io\n"
                "  \u2022 Podman Desktop  https://podman-desktop.io\n"
                f"Original error: {exc}"
            ) from exc

    # ── Linux (and anything else) ─────────────────────────────────────────────
    return docker.from_env()
