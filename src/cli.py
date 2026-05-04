import argparse

from .docker_manager import uninstall_docker_assets
from .main import main as run_app
from .setup_env import ensure_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mark2tex")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("tui", help="Abrir a interface TUI")
    subparsers.add_parser("doctor", help="Verificar dependências")
    subparsers.add_parser("uninstall", help="Remover artefatos Docker do Mark2TeX")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "tui"

    if command == "doctor":
        ensure_environment(check_only=True)
        return

    if command == "uninstall":
        uninstall_docker_assets()
        print("Agora remova o pacote com: pipx uninstall mark2tex")
        return

    ensure_environment()
    run_app()
