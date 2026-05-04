import os
import platform
import subprocess
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound

IMAGE_NAME = "mark2tex:latest"


class DockerManager:
    def __init__(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.bin_dir = self.project_root / "bin"
        self.templates_dir = self.project_root / "templates"

    def compile(self, input_file: str, template: str):
        cwd = Path.cwd().resolve()
        input_path = cwd / input_file
        build_sh = (self.bin_dir / "build.sh").resolve()
        templates_dir = self.templates_dir.resolve()

        if not input_path.exists():
            yield f"❌ Error: Input file '{input_file}' not found."
            return

        command = [
            "docker",
            "run",
            "--rm",
            "-i",
            "--mount",
            f"type=bind,src={cwd},dst=/app",
            "--mount",
            f"type=bind,src={build_sh},dst=/opt/mark2tex/build.sh,readonly",
            "--mount",
            f"type=bind,src={templates_dir},dst=/app/templates,readonly",
            IMAGE_NAME,
            "stdbuf",
            "-oL",
            "bash",
            "/opt/mark2tex/build.sh",
            f"/app/{Path(input_file).name}",
            template,
        ]

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
            yield f"\n❌ Error: Docker process exited with code {process.returncode}"


def uninstall_docker_assets() -> None:
    try:
        client = docker.from_env()
        image = client.images.get(IMAGE_NAME)
        client.images.remove(image.id, force=True)
        print(f"Imagem {IMAGE_NAME} removida com sucesso.")
    except ImageNotFound:
        print("Imagem Docker do Mark2TeX não encontrada.")
    except DockerException as exc:
        print(f"Erro ao remover imagem Docker: {exc}")
