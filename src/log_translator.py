import re

from .i18n import t

# ──────────────────────────────────────────────────────────────────────────────
# Padrões compilados uma única vez (performance)
_RE_PROGRESS      = re.compile(r"^PROGRESS:(\d+)%$")
_RE_PAGE_NUMS     = re.compile(r"^(\[\d+\]\s*)+$")
_RE_OVERFULL      = re.compile(
    r"^(Overfull|Underfull) \\hbox \((.+?)\) in paragraph at lines (\d+)--(\d+)"
)
_RE_LATEX_ERROR   = re.compile(r"^! LaTeX Error: (.+)")
_RE_GENERIC_ERROR = re.compile(r"^! (.+)")
_RE_LINE_REF      = re.compile(r"^l\.(\d+)\s*(.*)")
_RE_RUN_NUMBER    = re.compile(r"^Run number (\d+) of rule '(.+?)'")
_RE_RUNNING       = re.compile(r"^Running '(.+?)'")
_RE_RULE_CHANGE   = re.compile(r"^Rule '(.+?)': ")
_RE_LATEXMK       = re.compile(r"^Latexmk: (.+)")
_RE_DOC_CLASS     = re.compile(r"^Document Class: (\S+)")
_RE_OUTPUT_WRITTEN = re.compile(r"^Output written on (\S+) \((\d+) pages,")
_RE_PKG_WARN      = re.compile(r"^Package (\w+) Warning: (.+)")
_RE_LATEX_WARN    = re.compile(r"^LaTeX Warning: (.+)")
_RE_HOOKS_WARN    = re.compile(r"^LaTeX hooks Warning:")
_RE_MISSING_CHAR  = re.compile(r"^Missing character: There is no")
_RE_STY_PATH      = re.compile(r"^\(?/?(/usr/share/texlive|/etc/texmf|/usr/local/texlive)")
_RE_FONT_DEBUG    = re.compile(r"^(\\TU/|\\OT1/|\\T1/|\\TS1/)")
_RE_BRACKET_JUNK  = re.compile(r"^[\[\]\s]+$")
_RE_ABNT_DIVIDER  = re.compile(r"^-{30,}$")
_RE_PATH_ONLY     = re.compile(r"^\s*'?[\w./\\-]+\.(tex|aux|bbl|lof|lot|toc|log|xdv|pdf)'?\s*$")


def log_translator(line: str) -> str | None:
    """
    Receives a raw LaTeX/latexmk log line and returns:
      - None             -> suppress (do not display in console)
      - "__PROGRESS__N"  -> update progress bar to N%
      - str              -> translated message to display
    """
    stripped = line.strip()

    if not stripped:
        return None

    # ── Diretiva PROGRESS ────────────────────────────────────────────────────────────
    m = _RE_PROGRESS.match(stripped)
    if m:
        return f"__PROGRESS__{m.group(1)}"

    # ── Mensagens próprias do script (emojis) — passam direto ──────────────────
    first_char = stripped[0]
    if ord(first_char) > 127 and first_char not in ("(", "\\", "/"):
        return stripped

    # ── Suprimir: caminhos de pacotes .sty / .cls / etc. ────────────────────
    if _RE_STY_PATH.match(stripped):
        return None
    if stripped.startswith("/usr/share/texlive") or stripped.startswith("/etc/texmf"):
        return None

    if re.match(r"^-{3,}$", stripped) or re.match(r"^\*{3,}$", stripped):
        return None
    if _RE_ABNT_DIVIDER.match(stripped):
        return None
    if _RE_PAGE_NUMS.match(stripped):
        return None
    if _RE_BRACKET_JUNK.match(stripped) and "[" in stripped:
        return None
    if _RE_MISSING_CHAR.match(stripped):
        return None
    if stripped.startswith("flt;mapping=tex-text;"):
        return None
    if _RE_HOOKS_WARN.match(stripped):
        return None
    if stripped.startswith("(hooks)"):
        return None
    if _RE_FONT_DEBUG.match(stripped):
        return None

    _LAYOUT_PREFIXES = (
        "Stock height", "Top and edge", "Page height", "Text height",
        "Spine and edge", "Upper and lower", "Headheight", "Footskip",
        "Columnsep", "Marginparsep", "Sidecapsep", "Sidebarhsep",
        "Sidebarvsep", "Sidebarheight", "Sidefoothsep", "Sidefootvsep",
    )
    if stripped.startswith(_LAYOUT_PREFIXES):
        return None

    _SUPPRESS_EXACT = {
        r"\write18 enabled.", "entering extended mode", "(./output.tex",
        "Redoing nameref's sectioning", "Redoing nameref's label", "ment class",
        "For additional information on amsmath, use the `?' option.",
        "see the transcript file for additional information",
        "Transcript written on output.log.", "bibitemlist",
        "output.aux", "output.lof", "output.lot", "output.toc", "TeX engine is XeTeX",
    }
    if stripped in _SUPPRESS_EXACT:
        return None

    _SUPPRESS_PREFIX = (
        "L3 programming layer", "LaTeX2e <", "(|extractbb",
        "Package hyperref Warning: Rerun",
        "Package hyperref Warning: Suppressing empty link",
        "Changed files, or newly in use", "The top-level auxiliary file",
        "Em caso de dúvidas", "http://www.abntex",
        "See the LaTeX manual", "Type  H <return>",
    )
    if stripped.startswith(_SUPPRESS_PREFIX):
        return None

    if _RE_PATH_ONLY.match(stripped):
        return None
    if re.match(r"^\[\d+(\.\d+)?[a-z]*\]$", stripped):
        return None

    # ── Rc files ─────────────────────────────────────────────────────────────────
    if stripped == "Rc files read:":
        return t("log.config_reading")
    if re.match(r"^/etc/[Ll]atex", stripped):
        return t("log.config_file").format(path=stripped)

    # ── Output written ──────────────────────────────────────────────────────
    m = _RE_OUTPUT_WRITTEN.match(stripped)
    if m:
        return t("log.output_written").format(fmt=m.group(1), pages=m.group(2))

    # ── Latexmk ──────────────────────────────────────────────────────────────
    m = _RE_LATEXMK.match(stripped)
    if m:
        msg = m.group(1).strip()
        if msg.startswith("applying rule"):
            rule = re.search(r"'(.+?)'", msg)
            name: str = str(rule.group(1)) if rule else msg
            return t("log.applying_rule").format(name=name)
        if "This is Latexmk" in msg:
            ver = re.search(r"version: ([\d.]+)", msg)
            v = ver.group(1) if ver else ""
            return t("log.latexmk_version").format(ver=v)
        if "References changed" in msg:
            return t("log.refs_changed")
        if "Found bibliography files" in msg:
            f_match = re.search(r"files (.+)$", msg)
            fname = str(f_match.group(1)) if f_match else msg
            return t("log.bib_file").format(fname=fname)
        if "Found input bbl" in msg or "Log file says" in msg or "Examining" in msg:
            return None
        return t("log.latexmk_generic").format(msg=msg)

    # ── This is XeTeX / BibTeX ───────────────────────────────────────────────
    if stripped.startswith("This is XeTeX"):
        ver = re.search(r"Version ([\d.\-]+)", stripped)
        v = ver.group(1) if ver else ""
        return t("log.engine_xetex").format(ver=v)
    if stripped.startswith("This is BibTeX"):
        ver = re.search(r"Version ([\d.]+)", stripped)
        v = ver.group(1) if ver else ""
        return t("log.engine_bibtex").format(ver=v)

    # ── Document Class ───────────────────────────────────────────────────────────
    m = _RE_DOC_CLASS.match(stripped)
    if m:
        cls = m.group(1)
        if cls == "memoir":
            return None
        ver = re.search(r"v[-\d.]+", stripped)
        v = f" {ver.group(0)}" if ver else ""
        return t("log.doc_class").format(cls=cls, ver=v)

    # ── Rule / Run ──────────────────────────────────────────────────────────────
    if _RE_RULE_CHANGE.match(stripped):
        return None

    m = _RE_RUN_NUMBER.match(stripped)
    if m:
        return t("log.run_n").format(n=m.group(1), rule=m.group(2))

    m = _RE_RUNNING.match(stripped)
    if m:
        cmd = m.group(1)
        if "xelatex" in cmd:
            return t("log.running_xelatex")
        if "bibtex" in cmd:
            parts = cmd.split()
            arg = parts[-1] if parts else ""
            return t("log.running_bibtex").format(arg=arg)
        return t("log.running_cmd").format(cmd=cmd[:80])

    # ── Erros LaTeX ─────────────────────────────────────────────────────────────
    m = _RE_LATEX_ERROR.match(stripped)
    if m:
        return t("log.latex_error").format(msg=m.group(1))

    m = _RE_GENERIC_ERROR.match(stripped)
    if m:
        return t("log.error").format(msg=m.group(1))

    # ── Localização do erro: l.XX ───────────────────────────────────────────────
    m = _RE_LINE_REF.match(stripped)
    if m:
        lineno, ctx = m.group(1), m.group(2).strip()
        ctx_clean: str = re.sub(r"\\TU/\S+\s*", "", ctx).strip()
        if ctx_clean:
            return t("log.line_ref_ctx").format(n=lineno, ctx=ctx_clean)
        return t("log.line_ref").format(n=lineno)

    # ── Overfull / Underfull ────────────────────────────────────────────────────
    m = _RE_OVERFULL.match(stripped)
    if m:
        kind, amount, l1, l2 = m.groups()
        if kind == "Underfull":
            return None
        pts_match = re.search(r"[\d.]+", amount)
        if pts_match:
            try:
                if float(pts_match.group()) < 5.0:
                    return None
            except ValueError:
                pass
        return t("log.overfull").format(amount=amount, l1=l1, l2=l2)

    # ── Avisos de pacotes ───────────────────────────────────────────────────────
    m = _RE_PKG_WARN.match(stripped)
    if m:
        pkg, msg = m.group(1), m.group(2)
        if "Suppressing empty link" in msg or "Rerun" in msg:
            return None
        return t("log.pkg_warn").format(pkg=pkg, msg=msg)

    m = _RE_LATEX_WARN.match(stripped)
    if m:
        msg = m.group(1)
        if "Labels may have changed" in msg:
            return t("log.refs_changed")
        if "Empty thebibliography" in msg:
            return t("log.refs_empty")
        if "Rerun" in msg:
            return None
        return t("log.latex_warn").format(msg=msg)

    # ── BibTeX ────────────────────────────────────────────────────────────────────
    if stripped.startswith("The style file"):
        sty = stripped.replace("The style file", "").strip()
        return t("log.bib_style").format(sty=sty)
    if stripped.startswith("Database file"):
        db = re.sub(r"^Database file\s*#?\d*:?\s*", "", stripped)
        return t("log.bib_db").format(db=db)
    if "I found no commands" in stripped:
        return t("log.no_citations")
    if re.match(r"^There was[e]? \d+ error", stripped):
        return t("log.bib_errors").format(msg=stripped)

    if len(stripped) <= 2:
        return None
    if re.match(r"^[()./\\]+$", stripped):
        return None

    return stripped
