"""Mark2TeX CLI entry-point."""
from __future__ import annotations

import argparse
import sys

from .docker_manager import uninstall_docker_assets
from .main import main as run_app
from .setup_env import ensure_environment
from .yaml_injector import has_backup, restore_file


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

    restore_cmd = subparsers.add_parser(
        "restore",
        help="Restore a .md file to its state before YAML frontmatter was injected",
    )
    restore_cmd.add_argument(
        "file",
        metavar="FILE",
        help="Path to the .md file to restore",
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
            "[#e0a24a]⚠️  `mark2tex doctor` is deprecated — use `mark2tex check` instead.[/]"
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

    if command == "restore":
        file = args.file
        if not has_backup(file):
            print(f"✗ No backup found for '{file}'. Nothing to restore.", file=sys.stderr)
            sys.exit(1)
        success, msg = restore_file(file)
        if success:
            print(f"✔ {msg}")
        else:
            print(f"✗ {msg}", file=sys.stderr)
            sys.exit(1)
        return

    # Default: open TUI (with first-run onboarding if needed)
    ensure_environment()
    run_app()
