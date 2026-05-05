import shutil
import subprocess
import sys
from pathlib import Path

import docker
from docker.errors import DockerException, ImageNotFound

LOCAL_TAG = "mark2tex:latest"
HUB_IMAGE = "hylbert/mark2tex:latest"


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
    client = _get_docker_client()

    # 1. Imagem já existe localmente — nada a fazer
    try:
        client.images.get(LOCAL_TAG)
        return
    except ImageNotFound:
        pass

    # 2. Tenta puxar do Docker Hub
    if _pull_from_hub(client):
        return

    # 3. Fallback: build local a partir do Dockerfile bundled
    _build_locally(client)


def _get_docker_client():
    try:
        return docker.from_env()
    except DockerException as exc:
        print(f"Erro ao acessar o Docker: {exc}")
        sys.exit(1)


def _pull_from_hub(client) -> bool:
    """Tenta puxar a imagem do Docker Hub. Retorna True se bem-sucedido."""
    try:
        print("🐳 Imagem Mark2TeX não encontrada. Baixando do Docker Hub...")
        client.images.pull("hylbert/mark2tex", tag="latest")
        # Cria tag local para uso interno
        hub_img = client.images.get(HUB_IMAGE)
        hub_img.tag("mark2tex", tag="latest")
        print("✅ Imagem pronta.")
        return True
    except Exception:
        print("⚠️  Não foi possível acessar o Docker Hub. Tentando build local...")
        return False


def _build_locally(client) -> None:
    """Fallback: constrói a imagem a partir do Dockerfile no pacote ou no repo."""
    # Tenta usar o Dockerfile bundled dentro do pacote instalado
    bundled = Path(__file__).resolve().parent / "Dockerfile"
    # Se não estiver bundled, sobe dois níveis (clone do repositório)
    repo_root = Path(__file__).resolve().parents[1]
    build_path = str(bundled.parent) if bundled.exists() else str(repo_root)

    if not (Path(build_path) / "Dockerfile").exists():
        print("❌ Dockerfile não encontrado. Clone o repositório e execute 'make build-image'.")
        sys.exit(1)

    try:
        print("🔨 Construindo imagem localmente (pode demorar alguns minutos)...")
        client.images.build(path=build_path, tag=LOCAL_TAG, rm=True)
        print("✅ Imagem construída com sucesso.")
    except DockerException as exc:
        print(f"❌ Falha ao construir a imagem: {exc}")
        sys.exit(1)
