"""Tests for mark2tex.log_translator — stateless wrapper and stateful class."""
from __future__ import annotations

from mark2tex.log_translator import LogTranslator, log_translator

# ── Suppressions ─────────────────────────────────────────────────────────────

def test_empty_line_returns_none() -> None:
    assert log_translator("") is None

def test_whitespace_returns_none() -> None:
    assert log_translator("   ") is None

def test_page_numbers_suppressed() -> None:
    assert log_translator("[1] [2] [3]") is None

def test_bracket_junk_suppressed() -> None:
    assert log_translator("[][][]") is None

def test_sty_path_suppressed() -> None:
    assert log_translator("/usr/share/texlive/fonts/something.sty") is None

def test_font_debug_suppressed() -> None:
    assert log_translator(r"\TU/SomeFontData") is None

def test_hooks_warning_suppressed() -> None:
    assert log_translator("LaTeX hooks Warning: some hook message") is None

def test_separator_suppressed() -> None:
    assert log_translator("-----------------------------------") is None

def test_rule_change_suppressed() -> None:
    # _RE_RULE_CHANGE = r"^Rule '(.+?)': " — requires a space after the colon.
    # latexmk emits lines like "Rule 'xelatex': run 1" (content after colon).
    assert log_translator("Rule 'xelatex': run 1") is None

def test_xdvipdfmx_suppressed() -> None:
    assert log_translator("xdvipdfmx: fatal error: ...") is None

def test_document_class_memoir_suppressed() -> None:
    assert log_translator("Document Class: memoir 2023/01/01") is None

def test_missing_char_suppressed() -> None:
    assert log_translator("Missing character: There is no á in font xyz") is None

def test_layout_prefix_suppressed() -> None:
    assert log_translator("Stock height and width") is None

def test_very_short_line_suppressed() -> None:
    assert log_translator("ab") is None

def test_path_only_suppressed() -> None:
    assert log_translator("./output.tex") is None

def test_abnt_divider_suppressed() -> None:
    assert log_translator("-" * 35) is None

def test_etc_texmf_path_suppressed() -> None:
    assert log_translator("/etc/texmf/something.cfg") is None

# ── Build status lines ────────────────────────────────────────────────────────

def test_build_starting_translated() -> None:
    result = log_translator("\U0001f680 Starting build for doc.md using template tcc-abnt...")
    assert result is not None
    assert "doc.md" in result or "tcc-abnt" in result

def test_build_md_converted_translated() -> None:
    result = log_translator("\u2705 Markdown converted to LaTeX.")
    assert result is not None

def test_build_full_build_translated() -> None:
    result = log_translator("\U0001f527 Full build: no previous cache found.")
    assert result is not None

def test_build_incremental_translated() -> None:
    result = log_translator("\u26a1 Incremental build: reusing latexmk cache from previous run.")
    assert result is not None

def test_build_compiling_pdf_translated() -> None:
    result = log_translator("\U0001f528 Compiling PDF with latexmk...")
    assert result is not None

def test_build_pdf_ok_translated() -> None:
    result = log_translator("\u2705 PDF generated successfully: output.pdf")
    assert result is not None
    assert "output.pdf" in result

def test_build_pdf_error_translated() -> None:
    result = log_translator("\u274c Error: PDF was not generated.")
    assert result is not None

def test_build_complete_translated() -> None:
    result = log_translator("\U0001f389 Process complete!")
    assert result is not None

def test_build_cleaning_translated() -> None:
    result = log_translator("\U0001f9f9 Cleaning up ephemeral build files...")
    assert result is not None

def test_build_warn_no_state() -> None:
    result = log_translator("\u26a0\ufe0f Build failed with no latexmk state")
    assert result is not None

def test_build_warn_state_kept() -> None:
    result = log_translator("\u26a0\ufe0f Build failed but latexmk state preserved")
    assert result is not None

# ── PROGRESS ─────────────────────────────────────────────────────────────────

def test_progress_directive() -> None:
    assert log_translator("PROGRESS:75%") == "__PROGRESS__75"

# ── LaTeX errors ─────────────────────────────────────────────────────────────

def test_latex_error_translated() -> None:
    result = log_translator("! LaTeX Error: File not found.")
    assert result is not None and "\u2717" in result

def test_generic_error_translated() -> None:
    result = log_translator("! Undefined control sequence.")
    assert result is not None and "\u2717" in result

def test_error_with_hint_appended() -> None:
    result = log_translator("! LaTeX Error: Undefined control sequence.")
    assert result is not None and "\u2014" in result

def test_latex_error_no_hint_when_no_match() -> None:
    result = log_translator("! LaTeX Error: Something completely unknown happened.")
    assert result is not None
    # No hint dash when nothing matches
    assert "\u2014" not in result

# ── Stateful _after_error + l.N line ─────────────────────────────────────────

def test_line_ref_after_error_includes_location() -> None:
    tr = LogTranslator()
    tr.translate("! LaTeX Error: File not found.")
    result = tr.translate("l.42 \\unknownmacro")
    assert result is not None and "42" in result

def test_line_ref_without_error_context_still_shows_line() -> None:
    tr = LogTranslator()
    result = tr.translate("l.10")
    assert result is not None and "10" in result

def test_line_ref_without_context_fragment() -> None:
    """l.N with no trailing text uses the shorter format."""
    tr = LogTranslator()
    result = tr.translate("l.5")
    assert result is not None and "5" in result

def test_after_error_reset_on_empty_line() -> None:
    tr = LogTranslator()
    tr.translate("! LaTeX Error: Something.")
    tr.translate("")  # empty line resets state
    result = tr.translate("l.99")
    # Still shown as a bare line-ref (not indented continuation)
    assert result is not None and "99" in result

# ── Suppression continuation ─────────────────────────────────────────────────

def test_continuation_line_after_suppress_prefix_is_hidden() -> None:
    """A multi-line suppress block hides the continuation line."""
    tr = LogTranslator()
    # First line ends without '.' so continuation tracking is activated
    tr.translate("L3 programming layer: something going on")
    result = tr.translate("and this is the continuation that goes on")
    assert result is None

def test_continuation_ends_when_line_ends_with_period() -> None:
    tr = LogTranslator()
    tr.translate("L3 programming layer: something going on")
    tr.translate("continuation ends here.")  # ends with '.' → stops suppression
    # Next line must NOT be suppressed
    result = tr.translate("PROGRESS:10%")
    assert result == "__PROGRESS__10"

# ── Overfull / Underfull ──────────────────────────────────────────────────────

def test_overfull_hbox_translated() -> None:
    result = log_translator("Overfull \\hbox (20.0pt too wide) in paragraph at lines 42--45")
    assert result is not None and "\u26a0\ufe0f" in result

def test_small_overfull_hbox_suppressed() -> None:
    assert log_translator("Overfull \\hbox (2.0pt too wide) in paragraph at lines 10--11") is None

def test_underfull_hbox_badness_suppressed() -> None:
    assert log_translator("Underfull \\hbox (badness 1000) in paragraph at lines 5--6") is None

def test_underfull_hbox_small_pts_suppressed() -> None:
    assert log_translator("Underfull \\hbox (10.0pt too narrow) in paragraph at lines 1--2") is None

def test_underfull_hbox_large_pts_shown() -> None:
    result = log_translator("Underfull \\hbox (20.0pt too narrow) in paragraph at lines 1--2")
    assert result is not None

# ── Output written ────────────────────────────────────────────────────────────

def test_output_written_translated() -> None:
    result = log_translator("Output written on output.pdf (10 pages, 12345 bytes).")
    assert result is not None and "10" in result

# ── Latexmk ──────────────────────────────────────────────────────────────────

def test_latexmk_references_changed() -> None:
    result = log_translator("Latexmk: References changed.")
    assert result is not None and "\U0001f504" in result

def test_latexmk_version_translated() -> None:
    result = log_translator("Latexmk: This is Latexmk, John Collins, version: 4.79.")
    assert result is not None and "4.79" in result

def test_latexmk_applying_rule() -> None:
    result = log_translator("Latexmk: applying rule 'xelatex'")
    assert result is not None

def test_latexmk_bib_file() -> None:
    result = log_translator("Latexmk: Found bibliography files referencias.bib")
    assert result is not None

def test_latexmk_moving_noise_suppressed() -> None:
    assert log_translator("Latexmk: Moving 'output.pdf' to 'output.pdf'") is None

def test_latexmk_fls_noise_suppressed() -> None:
    assert log_translator("Latexmk: Fls file lists log file 'output.log', won't treat it as a source") is None

def test_latexmk_force_mode_translated() -> None:
    result = log_translator("Latexmk: Errors, in force_mode, so continuing")
    assert result is not None and "Errors, in force_mode" not in result

def test_latexmk_generic_fallback() -> None:
    result = log_translator("Latexmk: Some unknown message here")
    assert result is not None

# ── Running commands ─────────────────────────────────────────────────────────

def test_running_xelatex_translated() -> None:
    result = log_translator("Running 'xelatex output.tex'")
    assert result is not None and "xelatex" in result

def test_running_bibtex_translated() -> None:
    result = log_translator("Running 'bibtex output'")
    assert result is not None and "bibtex" in result.lower()

def test_running_generic_cmd() -> None:
    result = log_translator("Running 'makeglossaries output'")
    assert result is not None

# ── Document class ────────────────────────────────────────────────────────────

def test_document_class_translated() -> None:
    result = log_translator("Document Class: abntex2 2023/01/01")
    assert result is not None and "\U0001f4c4" in result

# ── Run number ───────────────────────────────────────────────────────────────

def test_run_number_translated() -> None:
    result = log_translator("Run number 2 of rule 'xelatex'")
    assert result is not None and "\U0001f504" in result

# ── Engines ───────────────────────────────────────────────────────────────────

def test_xelatex_engine_translated() -> None:
    result = log_translator("This is XeTeX, Version 3.141592653 (TeX Live 2023)")
    assert result is not None and "XeTeX" in result

def test_bibtex_engine_translated() -> None:
    result = log_translator("This is BibTeX, Version 0.99d")
    assert result is not None and "BibTeX" in result

# ── Rc / config files ─────────────────────────────────────────────────────────

def test_rc_files_read_translated() -> None:
    result = log_translator("Rc files read:")
    assert result is not None

def test_etc_latex_config_file() -> None:
    result = log_translator("/etc/latexmk/latexmkrc")
    assert result is not None

# ── fontspec errors ───────────────────────────────────────────────────────────

def test_fontspec_known_error_translated() -> None:
    result = log_translator('fontspec error: "font-not-found"')
    assert result is not None

def test_fontspec_unknown_code_uses_code_as_hint() -> None:
    result = log_translator('fontspec error: "some-unknown-code"')
    assert result is not None and "some-unknown-code" in result

# ── Package / LaTeX warnings ──────────────────────────────────────────────────

def test_package_warning_translated() -> None:
    result = log_translator("Package hyperref Warning: Anchor duplicate.")
    assert result is not None and "hyperref" in result

def test_package_warning_rerun_suppressed() -> None:
    assert log_translator("Package hyperref Warning: Rerun to get links right.") is None

def test_latex_warning_empty_bibliography() -> None:
    result = log_translator("LaTeX Warning: Empty `thebibliography' environment on input line 200.")
    assert result is not None

def test_latex_warning_undefined_refs() -> None:
    result = log_translator("LaTeX Warning: There were undefined references.")
    assert result is not None

def test_latex_warning_labels_changed_suppressed() -> None:
    result = log_translator(
        "LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
    )
    assert result is None

def test_latex_generic_warning() -> None:
    result = log_translator("LaTeX Warning: Some unusual situation occurred.")
    assert result is not None

# ── BibTeX messages ───────────────────────────────────────────────────────────

def test_bibliography_style_translated() -> None:
    result = log_translator("The style file: abnt.bst")
    assert result is not None and "\U0001f4dd" in result

def test_database_file_translated() -> None:
    result = log_translator("Database file #1: referencias.bib")
    assert result is not None and "\U0001f4da" in result

def test_no_citations_found() -> None:
    result = log_translator("I found no commands")
    assert result is not None

def test_bib_errors_line_translated() -> None:
    result = log_translator("There was 1 error message")
    assert result is not None

def test_bibtex_warn_empty_field() -> None:
    result = log_translator("Warning--empty title in silva2024")
    assert result is not None and "title" in result

def test_bibtex_warn_missing_field() -> None:
    result = log_translator("Warning--missing author in jones2022")
    assert result is not None and "author" in result

def test_bibtex_warn_generic() -> None:
    result = log_translator("Warning--something unexpected happened")
    assert result is not None

# ── Missing image ─────────────────────────────────────────────────────────────

def test_missing_image_warning_returns_translated_message() -> None:
    result = log_translator("\u26a0\ufe0f MISSING_IMAGE:./assets/foto.png")
    assert result is not None and "foto.png" in result

def test_missing_image_warning_contains_path_with_spaces() -> None:
    result = log_translator("\u26a0\ufe0f MISSING_IMAGE:./my images/diagram.png")
    assert result is not None and "my images/diagram.png" in result

def test_missing_image_warning_is_not_suppressed() -> None:
    assert log_translator("\u26a0\ufe0f MISSING_IMAGE:missing.jpg") is not None

# ── Polyglossia continuation ──────────────────────────────────────────────────

def test_polyglossia_continuation_suppressed() -> None:
    result = log_translator('e="Pt-BR" to langtag')
    assert result is None

def test_polyglossia_continuation_s_for_suppressed() -> None:
    result = log_translator("s for pt-BR.")
    assert result is None
