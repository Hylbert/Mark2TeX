import hashlib
import os
import platform
import shutil
import subprocess
from importlib import resources
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound
from platformdirs import user_cache_dir, user_config_dir, user_data_dir

IMAGE_NAME = "mark2tex:latest"
IMAGE_HUB  = "hylbert/mark2tex:latest"

# Timeout in seconds for a single compilation run.
# Can be overridden via the MARK2TEX_TIMEOUT environment variable.
COMPILE_TIMEOUT = int(os.environ.get("MARK2TEX_TIMEOUT", "300"))


def _get_package_path() -> Path:
    """Return the root of the installed package (works in dev and pipx, Python 3.9+)."""
    return Path(str(resources.files("mark2tex")))


def _compute_cache_dir(abs_file: str) -> Path:
    """Return (and create) a per-document cache dir under the OS user-cache directory.

    Path pattern:
      Linux   : ~/.cache/mark2tex/<sha1>/
      macOS   : ~/Library/Caches/mark2tex/<sha1>/
      Windows : %LOCALAPPDATA%\\mark2tex\\Cache\\<sha1>\\

    The SHA-1 is computed from the absolute path of the .md file so each
    document gets an isolated bucket with no name collisions.
    """
    doc_hash = hashlib.sha1(abs_file.encode()).hexdigest()[:16]
    cache_dir = Path(user_cache_dir("mark2tex", appauthor=False)) / doc_hash
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


class DockerManager:
    def __init__(self) -> None:
        pkg = _get_package_path()
        self.bin_dir       = pkg / "bin"
        self.templates_dir = pkg / "templates"

    def list_templates(self) -> list[str]:
        """Return template names discovered from the bundled templates directory."""
        if not self.templates_dir.is_dir():
            return []
        return sorted(
            d.name
            for d in self.templates_dir.iterdir()
            if d.is_dir() and (d / "template.tex").exists()
        )

    def compile(
        self,
        input_file: str,
        template: str,
        font: str | None = None,
    ):
        cwd           = Path.cwd().resolve()
        input_path    = cwd / input_file
        abs_file      = str(input_path)
        build_sh      = (self.bin_dir / "build.sh").resolve()
        templates_dir = self.templates_dir.resolve()
        cache_dir     = _compute_cache_dir(abs_file)

        if not input_path.exists():
            yield f"\u274c Error: Input file '{input_file}' not found."
            return

        command = [
            "docker", "run", "--rm", "-i",
            "--env", "M2T_CACHE_DIR=/m2t-cache",
            "--mount", f"type=bind,src={cwd},dst=/app",
            "--mount", f"type=bind,src={build_sh},dst=/opt/mark2tex/build.sh,readonly",
            "--mount", f"type=bind,src={templates_dir},dst=/app/templates,readonly",
            "--mount", f"type=bind,src={cache_dir},dst=/m2t-cache",
            IMAGE_NAME,
            "stdbuf", "-oL", "bash", "/opt/mark2tex/build.sh",
            f"/app/{Path(input_file).name}",
            template,
        ]

        if font:
            command.extend(["--font", font])

        if platform.system() != "Windows":
            uid = os.getuid() if hasattr(os, "getuid") else None
            gid = os.getgid() if hasattr(os, "getgid") else None
            if uid is not None and gid is not None:
                command[3:3] = ["--user", f"{uid}:{gid}"]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        try:
            stdout, _ = process.communicate(timeout=COMPILE_TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()  # drain the pipe to avoid ResourceWarning
            yield (
                f"\u274c Timeout: compilation exceeded {COMPILE_TIMEOUT}s "
                "and was terminated. Set MARK2TEX_TIMEOUT to increase the limit."
            )
            return

        yield from stdout.splitlines(keepends=True)

        if process.returncode != 0:
            yield f"\n\u274c Error: Docker process exited with code {process.returncode}"


def uninstall_docker_assets() -> None:
    """Full cleanup: remove Docker images, user data dir, and user config dir."""
    from .i18n import t

    # ── Docker images ──────────────────────────────────────────────────
    try:
        client = docker.from_env()
        for tag in (IMAGE_HUB, IMAGE_NAME):
            try:
                client.images.remove(tag, force=True)
                print(t("uninstall.image_removed").format(tag=tag))
            except ImageNotFound:
                print(t("uninstall.image_not_found").format(tag=tag))
    except DockerException as exc:
        print(t("uninstall.docker_error").format(error=exc))

    # ── User data (backups, onboarding flag) ───────────────────────────────────
    data_dir = Path(user_data_dir("mark2tex", appauthor=False))
    if data_dir.exists():
        shutil.rmtree(data_dir, ignore_errors=True)
        print(t("uninstall.data_removed").format(path=data_dir))
    else:
        print(t("uninstall.data_not_found").format(path=data_dir))

    # ── User config (language, theme) ──────────────────────────────────────────
    config_dir = Path(user_config_dir("mark2tex", appauthor=False))
    if config_dir.exists():
        shutil.rmtree(config_dir, ignore_errors=True)
        print(t("uninstall.config_removed").format(path=config_dir))
    else:
        print(t("uninstall.config_not_found").format(path=config_dir))

    # ── Latexmk cache ────────────────────────────────────────────────────────
    cache_root = Path(user_cache_dir("mark2tex", appauthor=False))
    if cache_root.exists():
        shutil.rmtree(cache_root, ignore_errors=True)
        print(t("uninstall.cache_removed").format(path=cache_root))
    else:
        print(t("uninstall.cache_not_found").format(path=cache_root))

    # ── Final hint ────────────────────────────────────────────────────────
    print()
    print(t("uninstall.pipx_hint"))
