import re

from .i18n import t

# ──────────────────────────────────────────────────────────────────────────────
# Compiled patterns (module level — created once for performance)
_RE_PROGRESS    = re.compile(r"^PROGRESS:(\d+)%$")
_RE_PAGE_NUMS   = re.compile(r"^(\[\d+\]\s*)+$")
_RE_OVERFULL    = re.compile(
    r"^(Overfull|Underfull) \\hbox \((.+?)\) in paragraph at lines (\d+)--(\d+)"
)
_RE_LATEX_ERROR  = re.compile(r"^! LaTeX Error: (.+)")
_RE_GENERIC_ERROR = re.compile(r"^! (.+)")
_RE_LINE_REF     = re.compile(r"^l\.(\d+)\s*(.*)")
_RE_RUN_NUMBER   = re.compile(r"^Run number (\d+) of rule '(.+?)'")
_RE_RUNNING      = re.compile(r"^Running '(.+?)'")
_RE_RULE_CHANGE  = re.compile(r"^Rule '(.+?)': ")
_RE_LATEXMK      = re.compile(r"^Latexmk: (.+)")
_RE_DOC_CLASS    = re.compile(r"^Document Class: (\S+)")
_RE_OUTPUT_WRITTEN = re.compile(r"^Output written on (\S+) \((\d+) pages,")
_RE_PKG_WARN     = re.compile(r"^Package (\w+) Warning: (.+)")
_RE_LATEX_WARN   = re.compile(r"^LaTeX Warning: (.+)")
_RE_HOOKS_WARN   = re.compile(r"^LaTeX hooks Warning:")
_RE_MISSING_CHAR = re.compile(r"^Missing character: There is no")
_RE_STY_PATH     = re.compile(r"^\(?/?(/usr/share/texlive|/etc/texmf|/usr/local/texlive)")
_RE_FONT_DEBUG   = re.compile(r"^(\\TU/|\\OT1/|\\T1/|\\TS1/)")
_RE_BRACKET_JUNK = re.compile(r"^[\[\]\s]+$")
_RE_ABNT_DIVIDER = re.compile(r"^-{30,}$")
_RE_PATH_ONLY    = re.compile(r"^\s*'?[\w./\\-]+\.(tex|aux|bbl|lof|lot|toc|log|xdv|pdf)'?\s*$")
_RE_FONTSPEC_ERR = re.compile(r"^fontspec error: \"(.+?)\"")
_RE_BIBTEX_WARN  = re.compile(r"^Warning--(.*)")
_RE_XDVIPDFMX    = re.compile(r"^xdvipdfmx:")

# ──────────────────────────────────────────────────────────────────────────────
# Module-level constants (hoisted out of the translate loop)
_LAYOUT_PREFIXES = (
    "Stock height", "Top and edge", "Page height", "Text height",
    "Spine and edge", "Upper and lower", "Headheight", "Footskip",
    "Columnsep", "Marginparsep", "Sidecapsep", "Sidebarhsep",
    "Sidebarvsep", "Sidebarheight", "Sidefoothsep", "Sidefootvsep",
)

_SUPPRESS_EXACT: frozenset[str] = frozenset({
    r"\write18 enabled.",
    "entering extended mode",
    "(./output.tex",
    "Redoing nameref's sectioning",
    "Redoing nameref's label",
    "ment class",
    "For additional information on amsmath, use the `?' option.",
    "see the transcript file for additional information",
    "Transcript written on output.log.",
    "bibitemlist",
    "output.aux", "output.lof", "output.lot", "output.toc",
    "TeX engine is XeTeX",
})

_SUPPRESS_PREFIX = (
    "L3 programming layer",
    "LaTeX2e <",
    "(|extractbb",
    "Package hyperref Warning: Rerun",
    "Package hyperref Warning: Suppressing empty link",
    "Changed files, or newly in use",
    "The top-level auxiliary file",
    "Em caso de dúvidas",
    "http://www.abntex",
    "See the LaTeX manual",
    "Type  H <return>",
    # polyglossia internal font-feature noise — not actionable by the user
    "(polyglossia) Asking to add empty feature to latin font",
    # fontspec raw mapping lines that leak through (e.g. "n;language=dflt;mapping=tex-text;!")
    "n;language=dflt;mapping=tex-text;",
)

# Maps error message substrings to i18n hint keys.
# Order matters: more specific fragments must come before generic ones.
_ERROR_HINTS: tuple[tuple[str, str], ...] = (
    ("Undefined control sequence",   "log.hint_undefined_cmd"),
    ("Missing $$ inserted",           "log.hint_math_display"),
    ("Missing $ inserted",            "log.hint_math_mode"),
    ("Missing { inserted",            "log.hint_missing_open_brace"),
    ("Missing } inserted",            "log.hint_missing_close_brace"),
    ("Extra }, or forgotten $",       "log.hint_extra_brace"),
    ("Too many }'s",                  "log.hint_too_many_braces"),
    ("Runaway argument",              "log.hint_runaway_arg"),
    ("File ended while scanning",     "log.hint_unclosed_env"),
    ("Paragraph ended before",        "log.hint_blank_in_arg"),
    ("Missing \\begin{document}",     "log.hint_missing_begin_doc"),
    ("Can be used only in preamble",  "log.hint_usepackage_after_begin"),
    ("already defined",               "log.hint_cmd_already_defined"),
    ("Option clash",                  "log.hint_option_clash"),
    ("environment undefined",         "log.hint_env_undefined"),
    ("Too many unprocessed floats",   "log.hint_too_many_floats"),
    ("TeX capacity exceeded",         "log.hint_capacity_exceeded"),
    ("Emergency stop",                "log.hint_emergency_stop"),
    ("not found",                     "log.hint_file_not_found"),
    ("No such counter",               "log.hint_no_counter"),
    ("Double subscript",              "log.hint_double_subscript"),
    ("Double superscript",            "log.hint_double_superscript"),
    ("Misplaced alignment tab",       "log.hint_misplaced_tab"),
    ("Extra \\right",                 "log.hint_extra_right"),
    ("Missing delimiter",             "log.hint_missing_delimiter"),
    ("Display math should end",       "log.hint_display_math"),
    ("Dimension too large",           "log.hint_dimension_large"),
    ("Arithmetic overflow",           "log.hint_arithmetic_overflow"),
    ("Counter too large",             "log.hint_counter_large"),
    ("Missing number",                "log.hint_missing_number"),
    ("Illegal unit of measure",       "log.hint_illegal_unit"),
    ("Bad math environment delimiter","log.hint_bad_math_delim"),
    ("\\verb ended by end of line",   "log.hint_verb_newline"),
    ("\\caption outside float",       "log.hint_caption_outside_float"),
    ("Something's wrong",             "log.hint_missing_item"),
    ("Lonely \\item",                 "log.hint_lonely_item"),
    ("Too deeply nested",             "log.hint_too_nested"),
    ("Not in outer par mode",         "log.hint_not_outer_par"),
    ("This NFSS system",              "log.hint_nfss"),
    ("I can't find file",             "log.hint_cant_find_file"),
    ("I can't write on file",         "log.hint_cant_write_file"),
    ("Invalid character",             "log.hint_invalid_char"),
    ("Illegal parameter number",      "log.hint_illegal_param"),
    ("Wrong DVI mode driver",         "log.hint_wrong_driver"),
    ("Float(s) lost",                 "log.hint_floats_lost"),
    ("Bad \\line or \\vector",        "log.hint_bad_line_vector"),
    ("This can't happen",             "log.hint_internal_bug"),
)

# Maps fontspec error codes to i18n hint keys.
_FONTSPEC_HINTS: dict[str, str] = {
    "font-not-found":        "log.hint_font_not_found",
    "font-no-shape":         "log.hint_font_no_shape",
    "feature-not-available": "log.hint_font_feature",
    "script-not-exist":      "log.hint_font_script",
    "language-not-exist":    "log.hint_font_language",
}


def _get_error_hint(msg: str) -> str:
    """Return the translated hint for *msg*, or empty string if none matches."""
    for fragment, key in _ERROR_HINTS:
        if fragment in msg:
            return t(key)
    return ""


class LogTranslator:
    """
    Stateful translator for LaTeX/latexmk log lines.

    Keeps context between lines so that a ``! Error`` line and its
    subsequent ``l.N context`` line are merged into a single, unified
    console message.

    Usage::

        translator = LogTranslator()
        for raw_line in log_lines:
            result = translator.translate(raw_line)
            if result is not None:
                display(result)
    """

    def __init__(self) -> None:
        self._pending_error: str | None = None

    def translate(self, line: str) -> str | None:
        """
        Receive a raw log line and return:

        - ``None``              — suppress (do not show in console)
        - ``"__PROGRESS__N"``   — update progress bar to N%
        - ``str``               — translated message ready to display
        """
        stripped = line.strip()

        if not stripped:
            self._pending_error = None
            return None

        # ── PROGRESS directive ───────────────────────────────────────────────
        m = _RE_PROGRESS.match(stripped)
        if m:
            return f"__PROGRESS__{m.group(1)}"

        # ── Script-owned messages (emoji prefix) — pass through ─────────────
        first_char = stripped[0]
        if ord(first_char) > 127 and first_char not in ("(", "\\", "/"):
            return stripped

        # ── Suppress: .sty / .cls / TexLive system paths ─────────────────────
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
        if stripped.startswith(_LAYOUT_PREFIXES):
            return None
        if stripped in _SUPPRESS_EXACT:
            return None
        if stripped.startswith(_SUPPRESS_PREFIX):
            return None
        if _RE_PATH_ONLY.match(stripped):
            return None
        if re.match(r"^\[\d+(\.\d+)?[a-z]*\]$", stripped):
            return None
        if len(stripped) <= 2:
            return None
        if re.match(r"^[()./\\]+$", stripped):
            return None

        # ── xdvipdfmx messages — suppress (driver-level noise) ───────────────
        if _RE_XDVIPDFMX.match(stripped):
            return None

        # ── Merge pending error with its l.N location line ───────────────────
        m = _RE_LINE_REF.match(stripped)
        if m:
            lineno = m.group(1)
            ctx    = m.group(2).strip()
            ctx_clean: str = re.sub(r"\\TU/\S+\s*", "", ctx).strip()
            if self._pending_error:
                msg = self._pending_error
                self._pending_error = None
                if ctx_clean:
                    return t("log.error_at_line_ctx").format(
                        msg=msg, n=lineno, ctx=ctx_clean
                    )
                return t("log.error_at_line").format(msg=msg, n=lineno)
            # No pending error: display bare line reference
            if ctx_clean:
                return t("log.line_ref_ctx").format(n=lineno, ctx=ctx_clean)
            return t("log.line_ref").format(n=lineno)

        # ── Rc files ─────────────────────────────────────────────────────────
        if stripped == "Rc files read:":
            return t("log.config_reading")
        if re.match(r"^/etc/[Ll]atex", stripped):
            return t("log.config_file").format(path=stripped)

        # ── Output written ───────────────────────────────────────────────────
        m = _RE_OUTPUT_WRITTEN.match(stripped)
        if m:
            return t("log.output_written").format(fmt=m.group(1), pages=m.group(2))

        # ── Latexmk ──────────────────────────────────────────────────────────
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

        # ── This is XeTeX / BibTeX ───────────────────────────────────────────
        if stripped.startswith("This is XeTeX"):
            ver = re.search(r"Version ([\d.\-]+)", stripped)
            v = ver.group(1) if ver else ""
            return t("log.engine_xetex").format(ver=v)
        if stripped.startswith("This is BibTeX"):
            ver = re.search(r"Version ([\d.]+)", stripped)
            v = ver.group(1) if ver else ""
            return t("log.engine_bibtex").format(ver=v)

        # ── Document Class ───────────────────────────────────────────────────
        m = _RE_DOC_CLASS.match(stripped)
        if m:
            cls = m.group(1)
            if cls == "memoir":
                return None
            ver = re.search(r"v[-\d.]+", stripped)
            v = f" {ver.group(0)}" if ver else ""
            return t("log.doc_class").format(cls=cls, ver=v)

        # ── Rule / Run ───────────────────────────────────────────────────────
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

        # ── fontspec errors (XeLaTeX) ────────────────────────────────────────
        m = _RE_FONTSPEC_ERR.match(stripped)
        if m:
            code = m.group(1)
            hint_key = _FONTSPEC_HINTS.get(code, "")
            hint = t(hint_key) if hint_key else code
            return t("log.fontspec_error").format(code=code, hint=hint)

        # ── LaTeX errors ─────────────────────────────────────────────────────
        m = _RE_LATEX_ERROR.match(stripped)
        if m:
            msg  = m.group(1)
            hint = _get_error_hint(msg)
            base = t("log.latex_error").format(msg=msg)
            self._pending_error = f"{base} — {hint}" if hint else base
            return None  # held until l.N arrives

        m = _RE_GENERIC_ERROR.match(stripped)
        if m:
            msg  = m.group(1)
            hint = _get_error_hint(msg)
            base = t("log.error").format(msg=msg)
            self._pending_error = f"{base} — {hint}" if hint else base
            return None  # held until l.N arrives

        # ── Overfull / Underfull ─────────────────────────────────────────────
        m = _RE_OVERFULL.match(stripped)
        if m:
            kind, amount, l1, l2 = m.groups()
            pts_match = re.search(r"[\d.]+", amount)
            if pts_match:
                try:
                    pts = float(pts_match.group())
                    if kind == "Underfull" and pts < 15.0:
                        return None
                    if kind == "Overfull" and pts < 5.0:
                        return None
                except ValueError:
                    pass
            if kind == "Underfull":
                return t("log.underfull").format(amount=amount, l1=l1, l2=l2)
            return t("log.overfull").format(amount=amount, l1=l1, l2=l2)

        # ── Package / LaTeX warnings ─────────────────────────────────────────
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
            if "undefined references" in msg:
                return t("log.undefined_refs")
            return t("log.latex_warn").format(msg=msg)

        # ── BibTeX ───────────────────────────────────────────────────────────
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

        m = _RE_BIBTEX_WARN.match(stripped)
        if m:
            warn_msg = m.group(1).strip()
            if "empty" in warn_msg:
                field = re.search(r"empty (\w+) in", warn_msg)
                entry = re.search(r"in (\S+)$", warn_msg)
                f = field.group(1) if field else "?"
                e = entry.group(1) if entry else "?"
                return t("log.bib_empty_field").format(field=f, entry=e)
            if "missing" in warn_msg:
                field = re.search(r"missing (\w+) in", warn_msg)
                entry = re.search(r"in (\S+)$", warn_msg)
                f = field.group(1) if field else "?"
                e = entry.group(1) if entry else "?"
                return t("log.bib_missing_field").format(field=f, entry=e)
            return t("log.bib_warn").format(msg=warn_msg)

        return stripped


# ── Default instance — backward-compatible module-level wrapper ───────────────
_default_translator = LogTranslator()


def log_translator(line: str) -> str | None:
    """Module-level wrapper around the default LogTranslator singleton."""
    return _default_translator.translate(line)
