# Changelog

All notable changes to Mark2TeX are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Fixed
- **Docker working directory resolved from input file** (`fix/docker-cwd-input-file-path`): `cwd` was previously set to `Path.cwd()` — the terminal's working directory at launch — so the Docker bind mount pointed to the wrong directory whenever the `.md` file lived in a different folder. `cwd` is now derived from the resolved parent of `input_file`, ensuring the container always mounts the directory that actually contains the file and `/app/<filename>` is always reachable inside the container.
- **Stray `.fls` file left in user's working directory** (`fix/fls-file-written-to-user-directory`): latexmk always writes the file list (`.fls`) to `$out_dir` (`/app`) at the end of every run, even when `$emulate_aux` is enabled, because `$fls_file` is not affected by the aux emulation mechanism. The `.fls` is not required for incremental builds — latexmk uses `.fdb_latexmk` for that — so it is now unconditionally removed by `cleanup()` in `build.sh` after each compilation, keeping the user's working directory clean.
- **Docker templates mount collision** (`fix/docker-templates-mount-collision`): the bind mount for bundled templates was targeting `/app/templates`, which is inside the working-directory mount (`/app`). Docker materialised this path on the host, creating a spurious `templates/` folder in the user's current directory on every compilation run. The mount destination was changed from `/app/templates` to `/opt/mark2tex/templates` — a path outside `/app` that is never reflected on the host filesystem. The `MARK2TEX_TEMPLATE_DIR` environment variable and `build.sh` fallback were updated to match. Custom templates added to the local package directory remain immediately available without rebuilding the Docker image, as the bind mount overlays the baked-in copy at runtime.

---

## [0.3.0] — 2026-05-07

### Added
- Granular progress bar driven by `PROGRESS:N%` tokens emitted by `build.sh` at each compilation phase (`10 → 40 → 50 → 60 → 75 → 88 → 94 → 100`). The TUI progress bar now advances in meaningful steps aligned to actual build stages (Pandoc conversion, latexmk initialisation, each xelatex pass, xdvipdfmx rendering).
- `_PROGRESS_MILESTONES` module-level constant and `_bump_ceiling()` helper in `app.py`: define the ordered sequence of official milestone values so that the bump heuristic always knows the ceiling for the current phase.
- Milestone-aware `progress_bump`: warning/error lines (`⚠️`, `❌`, `🔄`) still animate the progress bar between official milestones, but are now capped at `next_milestone − 1`. This prevents the bar from overshooting a future milestone and then rewinding when the official token arrives — producing a strictly non-decreasing progress experience even on documents with 60+ overfull-hbox warnings per xelatex pass.
- `build.*` i18n keys in `i18n.py` (both `pt_BR` and `en_US`) for all status messages emitted by `build.sh`: `build.starting`, `build.md_converted`, `build.full_build`, `build.incremental`, `build.compiling_pdf`, `build.pdf_ok`, `build.pdf_error`, `build.complete`, `build.cleaning`, `build.warn_no_state`, `build.warn_state_kept`.
- YAML frontmatter injection flow: files without a YAML header are highlighted in amber in the TUI file list. A confirmation modal injects the required frontmatter before compilation. The original file is backed up to `~/.local/share/mark2tex/backups/` with an `index.json` manifest.
- `mark2tex restore <file>` CLI subcommand to roll back a file to its pre-injection state.
- Directory tree traversal in the TUI file panel: subdirectories are listed before `.md` files; pressing `Enter` on a folder enters it. A `../` entry at the top navigates to the parent directory. Navigation is rooted at the working directory where `mark2tex` was invoked. The panel title shows the current folder name.
- `frontmatter_validator` module (`mark2tex/frontmatter_validator.py`): validates YAML frontmatter before compilation. Returns a list of `ValidationError` dataclasses covering: missing required fields, placeholder values not filled in, `template` mismatch between frontmatter and TUI selection, and invalid `lang` codes. Never raises — malformed YAML returns a single `parse_error` instead of an exception.
- Frontmatter validation integrated into `compile_specific_document()`: warnings are shown in the TUI console before the Docker worker starts. Non-critical warnings (placeholders, lang) do not block the build; missing required fields abort early and show a clear message.
- `swap_template()` in `yaml_injector.py`: surgically patches the `template:` and `date:` fields when the user switches templates in the TUI. Common fields with user-filled values are preserved; missing fields for the new template are added with placeholders; fields exclusive to the old template are removed.
- `mark2tex clean [file]` CLI subcommand: with no argument wipes the entire latexmk cache root; with a file argument removes only that document's cache bucket.
- Latexmk incremental compilation: intermediate files (`.aux`, `.fdb_latexmk`, `.fls`, `.bbl`, `.xdv`) are persisted across runs in an OS-standard user cache directory (`~/.cache/mark2tex/<doc_hash>/` on Linux, `~/Library/Caches/mark2tex/<doc_hash>/` on macOS, `%LOCALAPPDATA%\\mark2tex\\Cache\\<doc_hash>\\` on Windows). The cache is mounted into the container via `--env M2T_CACHE_DIR` + volume bind, reducing re-compilation time from ~18 s to ~6 s on a 15-page document after a single-line edit.
- Per-run `.latexmkrc` generated inside `CACHE_DIR` with `$emulate_aux = 1` for TeX Live 2022/4.76 compatibility (avoids the `-aux-directory` flag that xelatex rejects).
- Stale-cache guard in `build.sh`: if latexmk exits non-zero and no PDF is produced, the cache is wiped automatically so the next run starts clean.
- `DockerManager.abort()`: sends SIGKILL to the active container process and waits up to 5 s — called synchronously before scheduling a new Watch Mode worker to eliminate the race condition where the old container's cleanup trap deleted the `.tex` file written by the new Pandoc run.
- Compile subprocess timeout: default 300 s (5 min), overridable via `MARK2TEX_TIMEOUT` env var. On timeout the process is killed, the pipe drained, and a clear error message is shown in the TUI console.
- Exclusive compilation worker (`group="compile"`, `exclusive=True`): Textual cancels any prior worker before starting a new one, preventing parallel builds, interleaved log lines, and race conditions on the Docker subprocess.
- Watch Mode watcher improvements: temp/swap file filtering (`_TEMP_SUFFIXES`, `_IGNORE_DIRS` frozensets); debounce raised from 1.0 s to 1.5 s for editors that write in two stages (e.g. Obsidian); debug log is now conditional on `MARK2TEX_DEBUG` instead of always writing to `tui_console_debug.log`.
- Typography improvements for ABNT templates: `polyglossia` replaces `babel` in `tcc-abnt` and `artigo-abnt` for native XeLaTeX language support and correct pt-BR hyphenation; `setspace` + `\\OnehalfSpacing` enforces ABNT NBR 14724 / NBR 6022 1.5 line spacing; `csquotes` added to all templates for typographically correct quotation marks via `\\enquote{}` and `\\blockquote{}`.
- `mark2tex uninstall` now removes both `hylbert/mark2tex:latest` and `mark2tex:latest` Docker tags, the user data directory (`~/.local/share/mark2tex/`, including backups and onboarding flag), and the user config directory (`~/.config/mark2tex/`). All output respects the user's language preference via `i18n.t()`.
- `platformdirs` used throughout for cross-platform path resolution (user cache, data, and config directories).
- `PyYAML` and `types-pyyaml` added as explicit dependencies.
- CI: `pip` upgraded before audit step to fix CVE-2026-6357.

### Fixed
- Progress bar rewind bug: `progress_bump` previously had no ceiling, allowing warning-heavy compilations (e.g. 60+ overfull-hbox lines per xelatex pass) to push the bar past 99% during an early phase, causing it to visually snap back when the next official `PROGRESS:N%` token arrived. The bar is now strictly non-decreasing for all documents.
- `build.sh` status messages (`🚀 Starting build…`, `✅ Markdown converted…`, `🔧 Full build…`, `⚡ Incremental build…`, `🔨 Compiling PDF…`, `✅ PDF generated…`, `🎉 Process complete!`, `🧹 Cleaning up…`, `⚠️ Build failed…`) are now intercepted by `LogTranslator.translate()` before the generic emoji pass-through and mapped to `build.*` i18n keys, so they are properly translated according to the user's selected language.
- `tcc-abnt` template: `\\setdefaultlanguage` now uses `[variant=brazilian]{portuguese}` instead of the dynamic `{pt-BR}` value from the YAML `lang` field. The `pt-BR` BCP-47 code is not a valid polyglossia language identifier (`gloss-pt-BR.ldf` does not exist in TeX Live), which caused a LaTeX3 error on every compilation. The template is always Brazilian Portuguese, so the language setting is now fixed and correct.
- Mypy `no-any-return` error in `_load_index` resolved with `cast`.
- Removed `click` dependency; CLI now uses `argparse` only.
- Watch Mode race condition: `DockerManager.abort()` is now called synchronously before the new Pandoc run so the old container's cleanup trap cannot delete the freshly generated `.tex` file.
- `build.sh` latexmk cache preservation: cache is never wiped on successful builds; on failure it is only wiped when `.fdb_latexmk` is absent (i.e. latexmk never completed a full pass).
- `build.sh`: `--bibliography` is now only passed to Pandoc when the `.md` source contains actual citation markers (`[@key]` or `\\cite{`). This prevents Pandoc from emitting `\\bibliography{}` in citation-free documents and stops latexmk from scheduling Biber unnecessarily (eliminates the \"missing `\\item`\" / empty `.bbl` loop).
- `artigo-ieee` default `lang` changed from `en-US` to `english` — Babel does not accept BCP-47 locale codes.
- `WatcherManager` attributes annotated as `Optional[BaseObserver]` and `Optional[threading.Thread]` to satisfy mypy.
- Watcher `_log()` legacy method removed; logging now goes through the standard-library logger used by `app.py`.
- `latexmkrc` `$aux_dir`/`$out_dir` approach used instead of overriding `$xelatex` directly — prevents latexmk from losing track of `.fls`/`.xdv` files under TeX Live.
- Emoji echo in `build.sh` replaced with literal UTF-8 characters (bash does not interpret `\\uXXXX` in plain `echo`).
- `docker_manager.py`: removed extraneous `f`-prefix from static string.

### Tests
- Full test suite for `watcher.py`: `_TEMP_SUFFIXES`, `_IGNORE_DIRS`, `_is_temp_file()`, `_should_trigger()`, `on_modified`/`on_created`/`on_moved` callbacks, debounce behaviour, `WatcherManager` lifecycle (start/stop/idempotent stop).
- 30 tests for `frontmatter_validator`: happy paths for all templates, missing required fields, placeholder detection, `template_mismatch`, `invalid_lang`, `author` as list-of-dicts, multiple simultaneous errors, malformed YAML resilience.
- Tests for `swap_template()`: happy path (common fields preserved, new fields added with placeholder, old exclusive fields removed), no-op on files without frontmatter, returns `False` on unreadable file, bidirectional template swap (`artigo-ieee` ↔ `tcc-abnt`).
- Tests for compile timeout: `TimeoutExpired` path yields clear error message; `process.kill()` is called; pipe is drained; `MARK2TEX_TIMEOUT` env var overrides the module constant.
- `artigo-ieee` lang assertion updated from `en-US` to `english` to match the corrected default.

### Chore
- `platformdirs` added to dependencies.
- `PyYAML` and `types-pyyaml` added to dependencies.
- `.latexmkrc` written per-run inside `CACHE_DIR` and read via `-r` flag, never passed as a global config.

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
- `\\tightlist` stub in `doc-tecnica` template (fixes Pandoc compact-list rendering).
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `PULL_REQUEST_TEMPLATE.md`, issue templates.
- Rewritten `README.md` and `README.pt-BR.md` with CLI commands table, feature list, and roadmap.
- `docs/manual-de-uso.md` initial user manual.

### Fixed
- CRLF line endings in `build.sh` causing `$'\\r': command not found` on Windows Docker builds.
- `\\renewcommand{\\contentsline}[4]` conflict with `hyperref` 5-argument redefinition.
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
