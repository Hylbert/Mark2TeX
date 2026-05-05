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
_TEAL    = "#03656b"
_GREEN   = "#4caf87"
_YELLOW  = "#e0a24a"
_RED     = "#e05c5c"
_MUTED   = "#888888"
_WHITE   = "#fafafa"

_STATUS_ICON: dict[Status, tuple[str, str]] = {
    Status.OK:      ("✅", _GREEN),
    Status.WARNING: ("⚠️ ", _YELLOW),
    Status.ERROR:   ("❌", _RED),
}

_CHECK_LABELS: dict[str, dict[str, str]] = {
    "pt_BR": {
        "docker_binary":  "Docker (binário)",
        "docker_daemon":  "Docker (daemon)",
        "docker_image":   "Imagem mark2tex",
        "pandoc":         "Pandoc",
        "python_version": "Python",
        "disk_space":     "Espaço em disco",
    },
    "en_US": {
        "docker_binary":  "Docker binary",
        "docker_daemon":  "Docker daemon",
        "docker_image":   "Image mark2tex",
        "pandoc":         "Pandoc",
        "python_version": "Python",
        "disk_space":     "Disk space",
    },
}

_SUMMARY_LABELS: dict[str, dict[str, str]] = {
    "pt_BR": {
        "title":    "Mark2TeX — Diagnóstico do Sistema",
        "ok":       "OK",
        "warning":  "aviso",
        "error":    "erro",
        "plural_w": "avisos",
        "plural_e": "erros",
        "hint":     "Corrija os itens marcados com ❌ antes de compilar.",
        "all_ok":   "Tudo certo! Mark2TeX está pronto para uso.",
    },
    "en_US": {
        "title":    "Mark2TeX — System Check",
        "ok":       "OK",
        "warning":  "warning",
        "error":    "error",
        "plural_w": "warnings",
        "plural_e": "errors",
        "hint":     "Fix items marked with ❌ before compiling.",
        "all_ok":   "All good! Mark2TeX is ready to use.",
    },
}


def render_check_results(
    results: list[CheckResult],
    lang: str = "pt_BR",
    console: Console | None = None,
) -> int:
    """Render *results* to *console* and return an exit code (0 = all OK/warn, 1 = any error)."""
    con = console or Console()
    labels     = _CHECK_LABELS.get(lang, _CHECK_LABELS["en_US"])
    summary    = _SUMMARY_LABELS.get(lang, _SUMMARY_LABELS["en_US"])

    con.print()
    con.print(Rule(f"[bold {_TEAL}]{summary['title']}[/]", style=_TEAL))
    con.print()

    table = Table.grid(padding=(0, 2))
    table.add_column(width=3)   # icon
    table.add_column(width=20)  # label
    table.add_column()          # detail

    for r in results:
        icon_char, icon_color = _STATUS_ICON[r.status]
        label = labels.get(r.key, r.key)

        icon_text   = Text(icon_char, style=icon_color)
        label_text  = Text(label, style=f"bold {_WHITE}")
        detail_text = Text(r.detail, style=_MUTED)

        table.add_row(icon_text, label_text, detail_text)

        if r.extra:
            hint = Text(f"   {r.extra}", style=f"italic {_MUTED}")
            table.add_row(Text(""), Text(""), hint)

    con.print(table)
    con.print()
    con.print(Rule(style=_TEAL))

    n_ok   = sum(1 for r in results if r.status == Status.OK)
    n_warn = sum(1 for r in results if r.status == Status.WARNING)
    n_err  = sum(1 for r in results if r.status == Status.ERROR)

    ok_str   = f"[{_GREEN}]{n_ok} {summary['ok']}[/]"
    warn_str = (
        f"[{_YELLOW}]{n_warn} {summary['warning' if n_warn == 1 else 'plural_w']}[/]"
    )
    err_str  = (
        f"[{_RED}]{n_err} {summary['error' if n_err == 1 else 'plural_e']}[/]"
    )
    con.print(Padding(f"{ok_str}  ·  {warn_str}  ·  {err_str}", (0, 0, 0, 2)))
    con.print()

    if n_err == 0:
        con.print(Padding(f"[{_GREEN}]{summary['all_ok']}[/]", (0, 0, 1, 2)))
    else:
        con.print(Padding(f"[{_RED}]{summary['hint']}[/]", (0, 0, 1, 2)))

    return 1 if n_err > 0 else 0
