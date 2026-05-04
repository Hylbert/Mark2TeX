
import pytest


@pytest.fixture
def sample_md_file(tmp_path):
    md = tmp_path / "test_doc.md"
    md.write_text(
        "---\ntitle: Test\nauthor: Author\n---\n\n# Introdução\n\nTexto de teste.\n"
    )
    return md

@pytest.fixture
def sample_latex_log():
    return [
        "! LaTeX Error: File `package.sty` not found.",
        "l.15 \\usepackage{package}",
        "[1] [2] [3]",
        "Output written on output.pdf (2 pages, 5678 bytes).",
    ]
