import os
import platform
import subprocess
from importlib import resources
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound

IMAGE_NAME = "mark2tex:latest"


def _get_package_path() -> Path:
    """Return the root of the installed src/ package (works both in dev and pipx)."""
    with resources.path("src", "__init__.py") as p:
        return p.parent


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
        build_sh      = (self.bin_dir / "build.sh").resolve()
        templates_dir = self.templates_dir.resolve()

        if not input_path.exists():
            yield f"\u274c Error: Input file '{input_file}' not found."
            return

        command = [
            "docker", "run", "--rm", "-i",
            "--mount", f"type=bind,src={cwd},dst=/app",
            "--mount", f"type=bind,src={build_sh},dst=/opt/mark2tex/build.sh,readonly",
            "--mount", f"type=bind,src={templates_dir},dst=/app/templates,readonly",
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

        if process.stdout is not None:
            yield from process.stdout

        process.wait()
        if process.returncode != 0:
            yield f"\n\u274c Error: Docker process exited with code {process.returncode}"


def uninstall_docker_assets() -> None:
    try:
        client = docker.from_env()
        image  = client.images.get(IMAGE_NAME)
        client.images.remove(image.id, force=True)
        print(f"Imagem {IMAGE_NAME} removida com sucesso.")
    except ImageNotFound:
        print("Imagem Docker do Mark2TeX n\u00e3o encontrada.")
    except DockerException as exc:
        print(f"Erro ao remover imagem Docker: {exc}")
