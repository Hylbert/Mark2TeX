"""Mark2TeX CLI entry-point."""
from __future__ import annotations

import sys

import click

from .setup_env import setup_env
from .yaml_injector import has_backup, restore_file


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Mark2TeX — Markdown to LaTeX/PDF converter."""
    if ctx.invoked_subcommand is None:
        setup_env()
        from .app import Mark2TeXApp
        Mark2TeXApp().run()


@cli.command()
@click.argument("template", required=False)
def init(template: str | None) -> None:
    """Initialise a project directory with a template example."""
    from .onboarding import run_init
    run_init(template)


@cli.command()
def check() -> None:
    """Run a system check (Docker, Pandoc, disk space, etc.)."""
    from .checker import run_checks
    from .check_renderer import render_checks
    results = run_checks()
    render_checks(results)


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def restore(file: str) -> None:
    """Restore a .md file to its state before YAML frontmatter was injected."""
    if not has_backup(file):
        click.echo(f"No backup found for '{file}'. Nothing to restore.", err=True)
        sys.exit(1)
    success, msg = restore_file(file)
    if success:
        click.echo(f"✔ {msg}")
    else:
        click.echo(f"✗ {msg}", err=True)
        sys.exit(1)
