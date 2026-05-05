"""System health probes for `mark2tex check`.

All probes are pure functions that return ``CheckResult`` objects.
No Rich, no I/O side-effects — the renderer layer handles display.
Cross-platform: Linux, macOS, Windows.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Sequence


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class Status(str, Enum):
    OK      = "ok"
    WARNING = "warning"
    ERROR   = "error"


@dataclass
class CheckResult:
    key:    str          # i18n key suffix, e.g. "docker_binary"
    status: Status
    detail: str          # human-readable one-liner (already translated by caller)
    extra:  str = ""     # optional second line (tip / fix hint)


# ---------------------------------------------------------------------------
# Individual probes
# ---------------------------------------------------------------------------

def probe_docker_binary() -> CheckResult:
    """Check whether the `docker` CLI is on PATH."""
    path = shutil.which("docker")
    if path:
        return CheckResult("docker_binary", Status.OK, path)
    return CheckResult(
        "docker_binary",
        Status.ERROR,
        "not found",
        extra="Install Docker Desktop or Docker Engine: https://docs.docker.com/get-docker/",
    )


def probe_docker_daemon() -> CheckResult:
    """Check whether the Docker daemon is reachable."""
    if shutil.which("docker") is None:
        return CheckResult("docker_daemon", Status.ERROR, "skipped — docker binary missing")
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=8,
        )
        return CheckResult("docker_daemon", Status.OK, "active")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return CheckResult(
            "docker_daemon",
            Status.ERROR,
            "not running",
            extra="Start Docker Desktop or run: sudo systemctl start docker",
        )


def probe_docker_image() -> CheckResult:
    """Check whether the mark2tex:latest image exists locally."""
    try:
        import docker  # type: ignore
        from docker.errors import DockerException, ImageNotFound  # type: ignore

        client = docker.from_env()
        try:
            img = client.images.get("mark2tex:latest")
            # Report compressed size in MB
            size_mb = (img.attrs.get("Size") or 0) / (1024 ** 2)
            size_str = f"{size_mb:.0f} MB" if size_mb else "unknown size"
            return CheckResult("docker_image", Status.OK, f"mark2tex:latest ({size_str})")
        except ImageNotFound:
            return CheckResult(
                "docker_image",
                Status.WARNING,
                "not found locally",
                extra="Run `mark2tex` once to pull the image automatically.",
            )
        except DockerException as exc:
            return CheckResult("docker_image", Status.WARNING, f"daemon error: {exc}")
    except ImportError:
        return CheckResult("docker_image", Status.ERROR, "docker SDK not installed")


def probe_pandoc() -> CheckResult:
    """Check whether pandoc is available (optional — used only for fallback)."""
    path = shutil.which("pandoc")
    if path:
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version_line = result.stdout.splitlines()[0] if result.stdout else ""
            return CheckResult("pandoc", Status.OK, version_line or path)
        except Exception:
            return CheckResult("pandoc", Status.OK, path)
    return CheckResult(
        "pandoc",
        Status.WARNING,
        "not found (optional)",
        extra="Pandoc is bundled in the Docker image — host installation not required.",
    )


def probe_python_version() -> CheckResult:
    """Report current Python version (must be >= 3.10)."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 10):
        return CheckResult("python_version", Status.OK, version_str)
    return CheckResult(
        "python_version",
        Status.ERROR,
        f"{version_str} — requires Python 3.10+",
    )


def probe_disk_space(path: Path | None = None, threshold_gb: float = 2.0) -> CheckResult:
    """Check available disk space at *path* (defaults to home directory)."""
    check_path = path or Path.home()
    try:
        usage = shutil.disk_usage(check_path)
        free_gb = usage.free / (1024 ** 3)
        detail  = f"{free_gb:.1f} GB available"
        if free_gb >= threshold_gb:
            return CheckResult("disk_space", Status.OK, detail)
        return CheckResult(
            "disk_space",
            Status.WARNING,
            detail,
            extra=f"Less than {threshold_gb:.0f} GB free — Docker image may fail to pull.",
        )
    except OSError as exc:
        return CheckResult("disk_space", Status.WARNING, f"could not check: {exc}")


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

DEFAULT_PROBES = [
    probe_docker_binary,
    probe_docker_daemon,
    probe_docker_image,
    probe_pandoc,
    probe_python_version,
    probe_disk_space,
]


def run_all_checks(
    probes: Sequence = DEFAULT_PROBES,  # type: ignore[type-arg]
) -> list[CheckResult]:
    """Run every probe and return results in order."""
    return [p() for p in probes]
