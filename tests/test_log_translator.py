from src.log_translator import log_translator

# ── Supressões ────────────────────────────────────────────────────────────

def test_empty_line_returns_none():
    assert log_translator("") is None

def test_whitespace_returns_none():
    assert log_translator("   ") is None

def test_page_numbers_suppressed():
    assert log_translator("[1] [2] [3]") is None

def test_bracket_junk_suppressed():
    assert log_translator("[][][]") is None

def test_sty_path_suppressed():
    assert log_translator("/usr/share/texlive/fonts/something.sty") is None

def test_font_debug_suppressed():
    assert log_translator(r"\TU/SomeFontData") is None

def test_hooks_warning_suppressed():
    assert log_translator("LaTeX hooks Warning: some hook message") is None
def test_separator_suppressed():
    assert log_translator("-----------------------------------") is None

# ── Traduções ─────────────────────────────────────────────────────────────

def test_latex_error_translated():
    result = log_translator("! LaTeX Error: File not found.")
    assert result is not None
    assert "✗" in result
    assert "Erro LaTeX" in result

def test_generic_error_translated():
    result = log_translator("! Undefined control sequence.")
    assert result is not None
    assert "✗" in result

def test_output_written_translated():
    result = log_translator("Output written on output.pdf (10 pages, 12345 bytes).")
    assert result is not None
    assert "📄" in result
    assert "10 páginas" in result

def test_overfull_hbox_translated():
    result = log_translator("Overfull \\hbox (20.0pt too wide) in paragraph at lines 42--45")
    assert result is not None
    assert "⚠️" in result

def test_small_overfull_hbox_suppressed():
    result = log_translator("Overfull \\hbox (2.0pt too wide) in paragraph at lines 10--11")
    assert result is None

def test_underfull_hbox_suppressed():
    result = log_translator("Underfull \\hbox (badness 1000) in paragraph at lines 5--6")
    assert result is None

def test_package_warning_translated():
    result = log_translator("Package hyperref Warning: Anchor duplicate.")
    assert result is not None
    assert "⚠️" in result
    assert "hyperref" in result

def test_latex_warning_empty_bibliography():
    result = log_translator("LaTeX Warning: Empty `thebibliography' environment on input line 200.")
    assert result is not None
    assert "⚠️" in result

def test_progress_directive():
    result = log_translator("PROGRESS:75%")
    assert result == "__PROGRESS__75"

def test_xelatex_engine_translated():
    result = log_translator("This is XeTeX, Version 3.141592653 (TeX Live 2023)")
    assert result is not None
    assert "XeTeX" in result

def test_line_ref_with_context():
    result = log_translator("l.42 \\textbff{texto}")
    assert result is not None
    assert "42" in result

def test_latexmk_references_changed():
    result = log_translator("Latexmk: References changed.")
    assert result is not None
    assert "🔄" in result


def test_bibtex_engine_translated() -> None:
    result = log_translator("This is BibTeX, Version 0.99d")
    assert result is not None
    assert "BibTeX" in result

def test_document_class_translated() -> None:
    result = log_translator("Document Class: abntex2 2023/01/01")
    assert result is not None
    assert "📄" in result

def test_run_number_translated() -> None:
    result = log_translator("Run number 2 of rule 'xelatex'")
    assert result is not None
    assert "🔄" in result

def test_running_xelatex_translated() -> None:
    result = log_translator("Running 'xelatex output.tex'")
    assert result is not None
    assert "xelatex" in result

def test_bibliography_style_translated() -> None:
    result = log_translator("The style file: abnt.bst")
    assert result is not None
    assert "📝" in result

def test_database_file_translated() -> None:
    result = log_translator("Database file #1: referencias.bib")
    assert result is not None
    assert "📚" in result

def test_latex_warning_labels_changed_suppressed() -> None:
    # Comportamento real: string com "Rerun" é suprimida
    result = log_translator(
        "LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
    )
    assert result is None
