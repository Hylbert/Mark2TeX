# Changelog

All notable changes to Mark2TeX are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Font selection flag (`--font arial | helvetica | times | ubuntu`) via `build.sh` and TUI.
- `.gitattributes` enforcing LF line endings for all shell and text files.
- `tocloft`-native TOC styling in `doc-tecnica` template (removes `hyperref` conflict).
- `\tightlist` stub in `doc-tecnica` template (fixes Pandoc compact-list rendering).

### Fixed
- CRLF line endings in `build.sh` causing `$'\r': command not found` on Windows Docker builds.
- `\renewcommand{\contentsline}[4]` conflict with `hyperref` 5-argument redefinition.

---

## [0.1.0] — 2025-01-01

### Added
- Initial release of Mark2TeX.
- Dockerized XeLaTeX + Pandoc compilation pipeline.
- Interactive TUI built with [Textual](https://github.com/Textualize/textual): file browser, template selector, log console, progress bar.
- Watch mode for automatic recompilation on file save.
- Human-readable LaTeX log translation (`log_translator.py`).
- Templates: `tcc` (ABNT), `artigo-ieee` (IEEE), `doc-tecnica`, `projeto`, `apresentacao`.
- BibTeX bibliography support via `referencias.bib`.
- `pipx install -e .` installation flow.
- `make build` command to build the Docker image.
- GitFlow workflow with `main`, `develop`, `feature/*`, `hotfix/*`, and `release/*` branches.
