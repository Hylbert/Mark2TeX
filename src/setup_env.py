import shutil
import subprocess
import sys
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound

IMAGE_NAME = "mark2tex:latest"


def ensure_environment(check_only: bool = False) -> None:
    _check_docker_binary()
    _check_docker_daemon()

    if check_only:
        print("Docker encontrado e daemon acessível.")
        return

    _ensure_image()


def _check_docker_binary() -> None:
    if shutil.which("docker") is None:
        print("Docker não encontrado no PATH.")
        print("Instale o Docker Desktop ou Docker Engine para usar o Mark2TeX.")
        sys.exit(1)


def _check_docker_daemon() -> None:
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception:
        print("Docker encontrado, mas o daemon não está ativo/acessível.")
        print("Abra/inicie o Docker e tente novamente.")
        sys.exit(1)


def _ensure_image() -> None:
    try:
        client = docker.from_env()
        client.images.get(IMAGE_NAME)
    except ImageNotFound:
        print("Imagem do Mark2TeX não encontrada. Construindo pela primeira vez...")
        project_root = Path(__file__).resolve().parents[1]
        client.images.build(path=str(project_root), tag=IMAGE_NAME)
        print("Imagem Docker construída com sucesso.")
    except DockerException as exc:
        print(f"Erro ao acessar o Docker: {exc}")
        sys.exit(1)
