"""Rich console renderer for `mark2tex check` results.

Visual language matches the existing teal palette (#03656b / #4caf87 / #e05c5c).
No Textual dependency — pure Rich for terminal output.
"""
from __future__ import annotations

from rich.console import Console
from rich.padding import Padding
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .checker import CheckResult, Status

# Palette constants aligned with styles.tcss
_TEAL = "#03656b"
_GREEN = "#4caf87"
_YELLOW = "#e0a24a"
_RED = "#e05c5c"
_MUTED = "#888888"
_WHITE = "#fafafa"

_STATUS_ICON: dict[Status, tuple[str, str]] = {
    Status.OK: ("✅", _GREEN),
    Status.WARNING: ("⚠️ ", _YELLOW),
    Status.ERROR: ("❌", _RED),
}

_CHECK_LABELS: dict[str, dict[str, str]] = {
    "pt_BR": {
        "version": "Mark2TeX",
        "docker_binary": "Docker (binário)",
        "docker_daemon": "Docker (daemon)",
        "docker_image": "Imagem mark2tex",
        "pandoc": "Pandoc",
        "python_version": "Python",
        "disk_space": "Espaço em disco",
    },
    "en_US": {
        "version": "Mark2TeX",
        "docker_binary": "Docker binary",
        "docker_daemon": "Docker daemon",
        "docker_image": "Image mark2tex",
        "pandoc": "Pandoc",
        "python_version": "Python",
        "disk_space": "Disk space",
    },
}

_SUMMARY_LABELS: dict[str, dict[str, str]] = {
    "pt_BR": {
        "title": "Mark2TeX — Diagnóstico do Sistema",
        "ok": "OK",
        "warning": "aviso",
        "error": "erro",
        "plural_w": "avisos",
        "plural_e": "erros",
        "hint_err": "Corrija os itens marcados com ❌ antes de compilar.",
        "hint_warn": "Verifique os avisos acima antes de compilar.",
        "all_ok": "Tudo certo! Mark2TeX está pronto para uso.",
    },
    "en_US": {
        "title": "Mark2TeX — System Check",
        "ok": "OK",
        "warning": "warning",
        "error": "error",
        "plural_w": "warnings",
        "plural_e": "errors",
        "hint_err": "Fix items marked with ❌ before compiling.",
        "hint_warn": "Review the warnings above before compiling.",
        "all_ok": "All good! Mark2TeX is ready to use.",
    },
}


def _get_version(results: list[CheckResult]) -> str:
    """Extract version string from probe_version result, if present."""
    for r in results:
        if r.key == "version":
            return r.detail
    return ""


def render_check_results(
    results: list[CheckResult],
    lang: str = "pt_BR",
    console: Console | None = None,
) -> int:
    """Render *results* to *console*. Returns exit code: 0 = OK/warn, 1 = error."""
    con = console or Console()
    labels = _CHECK_LABELS.get(lang, _CHECK_LABELS["en_US"])
    summary = _SUMMARY_LABELS.get(lang, _SUMMARY_LABELS["en_US"])
    version = _get_version(results)

    title = summary["title"]
    if version:
        title = f"{title}  v{version}"

    con.print()
    con.print(Rule(f"[bold {_TEAL}]{title}[/]", style=_TEAL))
    con.print()

    table = Table.grid(padding=(0, 2))
    table.add_column(width=3)  # icon
    table.add_column(width=20)  # label
    table.add_column()  # detail

    # Collect image size to display alongside disk space
    image_mb: float = 0.0
    for r in results:
        if r.key == "docker_image":
            image_mb = r.meta.get("size_mb", 0.0)

    for r in results:
        # Skip version row from table — already shown in header
        if r.key == "version":
            continue

        icon_char, icon_color = _STATUS_ICON[r.status]
        label = labels.get(r.key, r.key)
        detail = r.detail

        # Augment disk_space row with image footprint when image exists
        if r.key == "disk_space" and image_mb > 0:
            suffix = f"imagem: {image_mb:.0f} MB" if lang == "pt_BR" else f"image: {image_mb:.0f} MB"
            detail = f"{detail}  ·  {suffix}"

        icon_text = Text(icon_char, style=icon_color)
        label_text = Text(label, style=f"bold {_WHITE}")
        detail_text = Text(detail, style=_MUTED)

        table.add_row(icon_text, label_text, detail_text)

        if r.extra:
            table.add_row(Text(""), Text(""), Text(f"   {r.extra}", style=f"italic {_MUTED}"))

    con.print(table)
    con.print()
    con.print(Rule(style=_TEAL))

    n_ok = sum(1 for r in results if r.status == Status.OK)
    n_warn = sum(1 for r in results if r.status == Status.WARNING)
    n_err = sum(1 for r in results if r.status == Status.ERROR)

    # Subtract version probe from OK count (not a real system check)
    version_ok = any(r.key == "version" and r.status == Status.OK for r in results)
    display_ok = n_ok - (1 if version_ok else 0)

    warn_label = summary["warning"] if n_warn == 1 else summary["plural_w"]
    err_label = summary["error"] if n_err == 1 else summary["plural_e"]

    ok_str = f"[{_GREEN}]{display_ok} {summary['ok']}[/]"
    warn_str = f"[{_YELLOW}]{n_warn} {warn_label}[/]"
    err_str = f"[{_RED}]{n_err} {err_label}[/]"
    con.print(Padding(f"{ok_str}  ·  {warn_str}  ·  {err_str}", (0, 0, 0, 2)))
    con.print()

    if n_err > 0:
        con.print(Padding(f"[{_RED}]{summary['hint_err']}[/]", (0, 0, 1, 2)))
        return 1
    if n_warn > 0:
        con.print(Padding(f"[{_YELLOW}]{summary['hint_warn']}[/]", (0, 0, 1, 2)))
        return 0
    con.print(Padding(f"[{_GREEN}]{summary['all_ok']}[/]", (0, 0, 1, 2)))
    return 0
