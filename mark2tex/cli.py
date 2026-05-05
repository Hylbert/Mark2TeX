import argparse
import sys

from .docker_manager import uninstall_docker_assets
from .main import main as run_app
from .setup_env import ensure_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mark2tex",
        description="Convert Markdown to professional PDF via LaTeX templates.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("tui",       help="Open the TUI dashboard (default)")
    subparsers.add_parser("check",     help="Run a full system health check")
    subparsers.add_parser("doctor",    help="Alias for 'check' (deprecated)")
    subparsers.add_parser("uninstall", help="Remove Mark2TeX Docker assets")

    init_cmd = subparsers.add_parser(
        "init",
        help="Copy a template + example file into the current directory",
    )
    init_cmd.add_argument(
        "--template",
        metavar="NAME",
        default=None,
        help="Template name to copy (e.g. artigo-ieee, tcc-abnt, doc-tecnica)",
    )

    return parser


def _run_check() -> None:
    """Execute all system probes and render a Rich report."""
    from rich.console import Console

    from . import config as cfg
    from .check_renderer import render_check_results
    from .checker import run_all_checks

    lang    = cfg.load().get("language", "pt_BR")
    results = run_all_checks()
    code    = render_check_results(results, lang=lang, console=Console())
    sys.exit(code)


def main() -> None:
    parser  = build_parser()
    args    = parser.parse_args()
    command = args.command or "tui"

    if command == "check":
        _run_check()
        return

    if command == "doctor":
        from rich.console import Console
        Console().print(
            "[#e0a24a]\u26a0\ufe0f  `mark2tex doctor` is deprecated — use `mark2tex check` instead.[/]"
        )
        _run_check()
        return

    if command == "uninstall":
        uninstall_docker_assets()
        print("Run `pipx uninstall mark2tex` to remove the package as well.")
        return

    if command == "init":
        from .onboarding import run_init
        run_init(template=getattr(args, "template", None))
        return

    # Default: open TUI (with first-run onboarding if needed)
    ensure_environment()
    run_app()
