# Changelog

All notable changes to Mark2TeX are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- YAML frontmatter injection flow: files without a YAML header are highlighted in amber in the TUI file list. A confirmation modal injects the required frontmatter before compilation. The original file is backed up to `~/.local/share/mark2tex/backups/` with an `index.json` manifest.
- `mark2tex restore <file>` CLI subcommand to roll back a file to its pre-injection state.
- Directory tree traversal in the TUI file panel: subdirectories are listed before `.md` files; pressing `Enter` on a folder enters it. A `../` entry at the top navigates to the parent directory. Navigation is rooted at the working directory where `mark2tex` was invoked. The panel title shows the current folder name.

### Fixed
- Mypy `no-any-return` error in `_load_index` resolved with `cast`.
- Removed `click` dependency; CLI now uses `argparse` only.

---

## [0.2.2] — 2026-05-05

### Added
- `mark2tex check` command: runs six system probes (Docker binary, Docker daemon, Docker image, Pandoc, Python version, disk space) and renders a Rich report in the project's teal palette. Exit code `1` when any ERROR probe fails, making it scriptable in CI.
- `mark2tex doctor` kept as a deprecated alias for `check` (prints a deprecation notice).
- `CheckResult` dataclass with `meta` dict; `probe_docker_image` now exposes `image_size_mb`.
- `probe_version` reads the installed package version via `importlib.metadata`.
- First-run onboarding screen (`OnboardingScreen`): shown automatically on the first launch via a `~/.local/share/mark2tex/.onboarding_done` flag. Includes an **"Initialise project here"** button that copies a ready-to-edit example `.md` into the current directory without leaving the TUI. On conflicts, the example is saved with an `_example` suffix to avoid overwriting existing files.
- After a successful in-TUI init, the file panel refreshes automatically without restarting the TUI.
- Rich Progress visual for Docker image pull on first run: per-layer progress bars showing download speed, file size, and estimated time remaining (`BarColumn + FileSizeColumn + TransferSpeedColumn + TimeRemainingColumn`).
- Local build fallback with a `Live` spinner when Docker Hub is unreachable.
- Graceful `KeyboardInterrupt` (Ctrl+C) handling during setup: exits with code 130.
- `docs/manual-de-uso.md` full rewrite: pipeline diagram, full YAML field tables per template, font metric table, BibTeX workflow, Watch Mode internals, Docker shell inspection guide, `mark2tex check` troubleshooting table, XeLaTeX error translation table, and GitHub Actions / GitLab CI / pre-commit integration examples.
- Unit tests for `checker.py`, `setup_env.py`, and `onboarding.py` (all mocked — no Docker daemon required).

### Fixed
- `check_renderer`: "all OK" message now only shown when there are 0 errors **and** 0 warnings.
- `checker.py` and `check_renderer.py`: Ruff E/F/W/I/UP cleanup (import order, alignment whitespace).

### Refactored
- Module renamed from `src/` to `mark2tex/` for correct PyPI packaging.
- `_get_package_path()` updated to use `importlib.resources.files('mark2tex')` (Python 3.12+).
- `pyproject.toml`: entry point, `packages.find`, `package-data`, and coverage paths updated.
- All test imports updated from `from src.` to `from mark2tex.`.

### CI
- `ci.yml` updated to reference `mark2tex/` instead of `src/`.
- `MANIFEST.in` updated accordingly.

---

## [0.2.1] — 2026-05-05

### Fixed
- `Dockerfile` COPY paths updated from `src/bin` and `src/templates` to `mark2tex/bin` and `mark2tex/templates` after the module rename.
- `test_docker_manager` updated to reflect new path resolution.

### Chore
- Bumped version to `0.2.1` to fix PyPI packaging of templates and `bin/`.

---

## [0.2.0] — 2026-05-05

### Added
- Automatic Docker image pull from Docker Hub on first run; local `Dockerfile` build as fallback when Hub is unreachable.
- `Dockerfile` bundled inside the `src/` package via `importlib.resources` so the fallback build works after `pipx install`.
- `pyproject.toml` `package_data` entry to include the bundled `Dockerfile`.
- Docker Hub push on merge to `main` via `docker-publish.yml` CI workflow.
- Font selection flag (`--font arial | helvetica | times | ubuntu`) via `build.sh` and TUI.
- `.gitattributes` enforcing LF line endings for all shell and text files.
- `tocloft`-native TOC styling in `doc-tecnica` template (removes `hyperref` conflict).
- `\tightlist` stub in `doc-tecnica` template (fixes Pandoc compact-list rendering).
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `PULL_REQUEST_TEMPLATE.md`, issue templates.
- Rewritten `README.md` and `README.pt-BR.md` with CLI commands table, feature list, and roadmap.
- `docs/manual-de-uso.md` initial user manual.

### Fixed
- CRLF line endings in `build.sh` causing `$'\r': command not found` on Windows Docker builds.
- `\renewcommand{\contentsline}[4]` conflict with `hyperref` 5-argument redefinition.
- `ca-certificates` added to Dockerfile to fix `curl` SSL error (exit code 77).
- `fontconfig` added to Dockerfile to fix `fc-cache not found` (exit code 127).
- Templates: replaced `Liberation Serif` / `Times New Roman` with `TeX Gyre Termes` for reliable font availability inside the Docker container (`tcc-abnt`, `artigo-abnt`, `doc-tecnica`, `projeto`).
- `ci.yml` smoke tests updated to use consistent local tag `mark2tex:latest`.

### Performance
- Dockerfile optimised: replaced `ttf-mscorefonts-installer` (external download) with `fonts-texgyre` (apt-native), removing the `debconf-set-selections` workaround.
- Added GHA layer cache (`cache-from` / `cache-to` with `gha` backend) to `docker-publish.yml`.

### Chore
- Personal filename removed from `Makefile`.
- `referencias.bib` neutralised (example content only).
- `.gitignore` expanded.

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
