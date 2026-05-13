"""Environment bootstrap for Mark2TeX.

Handles Docker binary check, daemon check, image pull (Docker Hub)
and local build fallback — all with Rich visual feedback.

Cross-platform: Linux, macOS, Windows.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from docker.errors import DockerException, ImageNotFound
from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    FileSizeColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.text import Text

from .docker_client import get_docker_client

# Palette aligned with check_renderer.py and styles.tcss
_TEAL = "#03656b"
_GREEN = "#4caf87"
_YELLOW = "#e0a24a"
_RED = "#e05c5c"
_MUTED = "#888888"
_WHITE = "#fafafa"

LOCAL_TAG = "mark2tex:latest"
HUB_IMAGE = "hylbert/mark2tex:latest"

_console = Console()


def ensure_environment(check_only: bool = False) -> None:
    _check_docker_binary()
    _check_docker_daemon()

    if check_only:
        _console.print(f"[{_GREEN}]✅  Docker encontrado e daemon acessível.[/]")
        return

    _ensure_image()


def _check_docker_binary() -> None:
    if shutil.which("docker") is None:
        _console.print(f"[{_RED}]❌  Docker não encontrado no PATH.[/]")
        _console.print(
            f"[{_MUTED}]Instale o Docker Desktop ou Docker Engine para usar o Mark2TeX.[/]"
        )
        sys.exit(1)


def _check_docker_daemon() -> None:
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception:  # noqa: BLE001
        _console.print(f"[{_RED}]❌  Docker encontrado, mas o daemon não está ativo/acessível.[/]")
        _console.print(f"[{_MUTED}]Abra/inicie o Docker e tente novamente.[/]")
        sys.exit(1)


def _ensure_image() -> None:
    client = _get_client()

    try:
        client.images.get(LOCAL_TAG)
        return
    except ImageNotFound:
        pass

    if _pull_from_hub(client):
        return

    _build_locally(client)


def _get_client():
    try:
        return get_docker_client()
    except DockerException as exc:
        _console.print(f"[{_RED}]❌  Erro ao acessar o Docker: {exc}[/]")
        sys.exit(1)


def _make_progress() -> Progress:
    """Build a Rich Progress instance with the project's visual palette."""
    return Progress(
        SpinnerColumn(style=_TEAL),
        TextColumn("{task.description}", style=_WHITE),
        BarColumn(bar_width=28, style=_MUTED, complete_style=_TEAL, finished_style=_GREEN),
        FileSizeColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=_console,
        transient=False,
    )


def _pull_from_hub(client) -> bool:
    """Pull image from Docker Hub with per-layer Rich progress. Returns True on success."""
    _console.print()
    _console.print(
        Text("🐳  Baixando imagem Mark2TeX do Docker Hub…", style=f"bold {_TEAL}")
    )
    _console.print(Text("    Isso pode levar alguns minutos na primeira vez.", style=_MUTED))
    _console.print()

    # layer_id → TaskID
    tasks: dict[str, TaskID] = {}

    try:
        with _make_progress() as progress:
            for event in client.api.pull(
                "hylbert/mark2tex", tag="latest", stream=True, decode=True
            ):
                status: str = event.get("status", "")
                layer: str = event.get("id", "")
                detail: dict = event.get("progressDetail", {})

                if not layer:
                    continue

                current: int = detail.get("current", 0)
                total: int = detail.get("total", 0)

                if status in ("Waiting", "Pulling fs layer") and layer not in tasks:
                    tasks[layer] = progress.add_task(
                        f"[{_MUTED}]{layer[:12]}[/]  {status}",
                        total=None,
                        visible=True,
                    )

                elif status == "Downloading" and layer in tasks:
                    if total:
                        progress.update(
                            tasks[layer],
                            description=f"[{_TEAL}]{layer[:12]}[/]  Downloading",
                            total=total,
                            completed=current,
                        )
                    else:
                        progress.update(
                            tasks[layer],
                            description=f"[{_TEAL}]{layer[:12]}[/]  Downloading",
                        )

                elif status == "Extracting" and layer in tasks:
                    progress.update(
                        tasks[layer],
                        description=f"[{_YELLOW}]{layer[:12]}[/]  Extracting",
                        total=total or None,
                        completed=current,
                    )

                elif status == "Pull complete" and layer in tasks:
                    progress.update(
                        tasks[layer],
                        description=f"[{_GREEN}]{layer[:12]}[/]  ✓ Done",
                        completed=progress.tasks[tasks[layer]].total or 1,
                        total=progress.tasks[tasks[layer]].total or 1,
                    )

    except KeyboardInterrupt:
        _console.print(f"\n[{_YELLOW}]⚠️   Download interrompido pelo usuário.[/]")
        sys.exit(130)
    except Exception:  # noqa: BLE001
        _console.print(
            f"[{_YELLOW}]⚠️   Não foi possível acessar o Docker Hub. Tentando build local…[/]"
        )
        return False

    # Tag local for internal use
    try:
        hub_img = client.images.get(HUB_IMAGE)
        hub_img.tag("mark2tex", tag="latest")
    except Exception:  # noqa: BLE001
        pass

    _console.print()
    _console.print(Text("✅  Imagem pronta.", style=f"bold {_GREEN}"))
    _console.print()
    return True


def _build_locally(client) -> None:
    """Fallback: build image from bundled Dockerfile with Rich Live spinner."""
    bundled = Path(__file__).resolve().parent / "Dockerfile"
    repo_root = Path(__file__).resolve().parents[1]
    build_path = str(bundled.parent) if bundled.exists() else str(repo_root)

    if not (Path(build_path) / "Dockerfile").exists():
        _console.print(
            f"[{_RED}]❌  Dockerfile não encontrado. "
            "Clone o repositório e execute 'make build-image'.[/]"
        )
        sys.exit(1)

    _console.print()
    _console.print(
        Text("🔨  Construindo imagem localmente…", style=f"bold {_TEAL}")
    )
    _console.print(Text("    Isso pode demorar alguns minutos.", style=_MUTED))
    _console.print()

    spinner = Progress(
        SpinnerColumn(style=_TEAL),
        TextColumn("{task.description}", style=_WHITE),
        console=_console,
        transient=False,
    )

    try:
        with Live(spinner, console=_console, refresh_per_second=10):
            task = spinner.add_task("Preparando build…", total=None)
            for chunk in client.api.build(path=build_path, tag=LOCAL_TAG, rm=True, decode=True):
                stream_line: str = chunk.get("stream", "").strip()
                error_line: str = chunk.get("error", "").strip()

                if error_line:
                    spinner.update(task, description=f"[{_RED}]{error_line[:72]}[/]")
                elif stream_line and stream_line != "\n":
                    if stream_line.lower().startswith("step"):
                        spinner.update(task, description=f"[{_TEAL}]{stream_line[:72]}[/]")

    except KeyboardInterrupt:
        _console.print(f"\n[{_YELLOW}]⚠️   Build interrompido pelo usuário.[/]")
        sys.exit(130)
    except DockerException as exc:
        _console.print(f"[{_RED}]❌  Falha ao construir a imagem: {exc}[/]")
        sys.exit(1)

    _console.print()
    _console.print(Text("✅  Imagem construída com sucesso.", style=f"bold {_GREEN}"))
    _console.print()
