<p align="center">
  <img src="assets/logo.png" alt="Mark2TeX" width="150" height="150">
</p>

<h1 align="center">Mark2TeX</h1>

<div align="center">
  <strong><span>English</span> | <a href="README.pt-BR.md">Português (Brasil)</a></strong>
</div>

<div align="center">
  <strong>Write Markdown. Get a polished academic PDF.</strong><br>
  A Dockerized pipeline with an interactive TUI for LaTeX-quality documents — no TeX installation required.
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/workflow-GitFlow-orange.svg" alt="GitFlow">
  <img src="https://img.shields.io/badge/version-SemVer-green.svg" alt="SemVer">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
  <a href="https://pypi.org/project/mark2tex/">
    <img src="https://img.shields.io/pypi/dm/mark2tex.svg" alt="PyPI Downloads">
  </a>
  <a href="https://coveralls.io/github/Hylbert/Mark2TeX?branch=develop">
    <img src="https://coveralls.io/repos/github/Hylbert/Mark2TeX/badge.svg?branch=develop" alt="Coverage Status">
  </a>
  <a href="https://pypi.org/project/mark2tex/">
    <img src="https://badge.fury.io/py/mark2tex.svg" alt="PyPI version">
  </a>
  <a href="https://snyk.io/test/github/Hylbert/Mark2TeX">
    <img src="https://snyk.io/test/github/Hylbert/Mark2TeX/badge.svg" alt="Known Vulnerabilities">
  </a>
</div>


<br>


<p align="center">
  <img src="https://github.com/user-attachments/assets/e2ebac18-6c4e-4048-b79c-66bc6d7fdddf" width="900" alt="Mark2TeX demo">
</p>


<br>

## What is Mark2TeX?

Mark2TeX is a command-line tool that converts Markdown files into publication-ready PDFs using Pandoc, XeLaTeX, and pre-built LaTeX templates — all inside a Docker container. You write plain text; Mark2TeX handles the typography.

**Why Mark2TeX instead of writing LaTeX directly?**

| | LaTeX | Mark2TeX |
|---|---|---|
| Learning curve | Steep | Write plain Markdown |
| Environment setup | 4 GB+ TeX distribution | Only Docker |
| Error messages | Cryptic logs | Human-readable translations |
| Live feedback | Manual re-run | Watch mode auto-recompiles |

## Quickstart

> **Why `pipx`?**
> Mark2TeX is a CLI tool, not a library. `pipx` installs Python CLI tools in
> isolated environments automatically — without polluting your system Python or
> requiring a manual `venv`. If you don't have `pipx` yet:
>
> ```bash
> # Ubuntu / Debian
> sudo apt install pipx && pipx ensurepath
>
> # macOS
> brew install pipx && pipx ensurepath
>
> # Windows (PowerShell)
> python -m pip install --user pipx
> python -m pipx ensurepath
> ```
>
> Restart your terminal after running `ensurepath`.

```bash
# 1 — install (requires Python 3.10+ and Docker)
pipx install mark2tex

# 2 — check your environment (recommended on first install)
mark2tex check

# 3 — open the TUI dashboard (Docker image is pulled automatically)
mark2tex
```


<p align="center">
  <img src="https://github.com/user-attachments/assets/3d4a666e-e4b0-470c-8677-936bf49289bd" width="900" alt="Mark2TeX pipx installation">
</p>


> **First run:** Mark2TeX automatically pulls the `mark2tex` image from Docker Hub with a
> **Rich visual progress bar** — one bar per image layer showing download speed, file size,
> and estimated time remaining. Requires an active internet connection; may take a few minutes
> depending on your speed. Subsequent runs reuse the cached image.
>
> **No internet?** If Docker Hub is unreachable, Mark2TeX falls back to building the image
> locally from the bundled `Dockerfile` (spinner shown during build steps).
> You can also run `make build-image` manually at any time.

> **Welcome screen:** On the very first launch, a welcome screen guides you through the
> workflow. Click **"Initialise project here"** to copy a ready-to-edit example `.md` file
> directly into your current directory — no need to leave the app. You can also run
> `mark2tex init` from the terminal at any time to do the same thing.

## CLI Commands

| Command | Description |
|---|---|
| `mark2tex` | Open the interactive TUI dashboard (default) |
| `mark2tex check` | Run a full system health check |
| `mark2tex init [--template NAME]` | Copy a template + example into the current directory |
| `mark2tex restore <file>` | Restore a `.md` file to its state before YAML injection |
| `mark2tex clean [file]` | Wipe the latexmk build cache — all docs or a specific one |
| `mark2tex uninstall` | Remove Docker images, user data, and config dirs — run before `pipx uninstall mark2tex` |
| `mark2tex doctor` | Alias for `check` *(deprecated — use `check`)* |

### `mark2tex check` — System Health Report

Runs six probes and prints a visual report:

```
──────────────── Mark2TeX — System Check  v0.2.2 ────────────────

✅   Mark2TeX          0.2.2
✅   Docker binary     /usr/bin/docker
✅   Docker daemon     active
✅   Image mark2tex    mark2tex:latest (1 143 MB)
⚠️   Pandoc            not found (optional)
                          Pandoc is bundled in the Docker image — host installation not required.
✅   Python            3.12.3
✅   Disk space        145.0 GB free (320.1 GB used / 465.1 GB total)  ·  image: 1 143 MB

─────────────────────────────────────────────────────────────────
  5 OK  ·  1 warning  ·  0 errors

  Review the warnings above before compiling.
```

Exit code `0` when no errors are found; exit code `1` when at least one error probe fails — making it scriptable in CI pipelines.


## TUI at a Glance

<p align="center">
  <img src="https://github.com/user-attachments/assets/036acf5a-d564-4173-9034-d603ec03f3ca" width="900" alt="Mark2TeX Watch Mode demo">
</p>


1. Select a `.md` file from the left panel.
2. Choose a template (`tcc-abnt`, `artigo-ieee`, `doc-tecnica`, `projeto`).
3. Optionally pick a font (`Liberation Serif`, `Liberation Sans`, `Nimbus Sans`, `Ubuntu`).
4. Press **`c`** to compile or **`w`** to toggle Watch Mode.
5. Preview the Markdown file
6. Monitor real-time console output

### Keyboard shortcuts

| Key | Action |
|---|---|
| `c` | Compile |
| `w` | Toggle Watch Mode |
| `Enter` | Enter folder / select file |
| `F1` / `?` | Help |
| `Esc` / `q` | Global menu |

## Features

- **Dockerized builds** — zero local LaTeX installation; identical output on every machine.
- **Interactive TUI** — file browser, template selector, real-time log console, and progress bar built with [Textual](https://github.com/Textualize/textual).
- **Directory navigation** — the file panel opens at the current working directory. Subdirectories are listed before `.md` files; press `Enter` on a folder to enter it. A `../` entry at the top of the list navigates back to the parent folder.
- **First-run onboarding** — welcome screen shown on the first launch with a built-in "Initialise project here" button that copies an example `.md` into your current directory without leaving the app.
- **Watch mode** — automatic recompilation on every file save; temp/swap files (`.swp`, `.bak`, `~`) are ignored; debounce of 1.5 s prevents double-triggers on two-stage saves (e.g. Obsidian).
- **Incremental builds** — latexmk persists intermediate files (`.aux`, `.fdb_latexmk`, `.fls`) in an OS-standard user cache directory. Re-compilation after a single-line edit takes ~6 s instead of ~18 s on a 15-page document.
- **Compile timeout** — a 5-minute timeout (overridable via `MARK2TEX_TIMEOUT`) prevents hanging builds from locking the UI indefinitely.
- **Exclusive worker** — pressing `c` twice or a Watch Mode trigger during a running build cancels the previous worker before starting a new one, eliminating interleaved log output.
- **Frontmatter validator** — before each compilation the YAML frontmatter is checked for missing required fields, unfilled placeholder values, template mismatches, and invalid `lang` codes. Warnings appear in the TUI console; critical errors abort the build early.
- **Template swap** — switching templates in the TUI surgically updates `template:` and `date:` in the frontmatter, adds missing fields with placeholders, and removes fields exclusive to the old template — all without touching the values you already filled in.
- **Human-readable logs** — raw XeLaTeX output is parsed and translated into plain-language messages.
- **Font selection** — choose between Liberation Sans (Arial-compatible), Nimbus Sans (Helvetica), Liberation Serif (Times-compatible), and Ubuntu per document.
- **Bibliography support** — BibTeX via Pandoc + XeLaTeX; just drop a `referencias.bib` alongside your `.md`. BibTeX is only invoked when actual citation markers are present in the source.
- **System health check** — `mark2tex check` diagnoses your environment before you compile.
- **Rich image pull progress** — per-layer progress bars with speed and ETA when pulling the Docker image on first run.
- **YAML frontmatter injection** — files without a YAML header are highlighted in amber in the TUI; a confirmation modal injects the frontmatter automatically before compilation. A backup is saved to `~/.local/share/mark2tex/backups/` and can be restored at any time with `mark2tex restore <file>`.
- **Build cache management** — `mark2tex clean [file]` removes the latexmk cache for all documents or a specific one.
- **ABNT-oriented workflow** — templates built around Brazilian academic standards, with `polyglossia` for correct pt-BR hyphenation and `setspace` for ABNT-required 1.5 line spacing.

## Available Templates

| Template | Purpose |
|---|---|
| `tcc-abnt` | Undergraduate thesis (ABNT) |
| `artigo-ieee` | IEEE conference paper |
| `artigo-abnt` | ABNT journal article |
| `doc-tecnica` | Technical documentation |
| `projeto` | Project proposal |

## Roadmap

- [x] System health check (`mark2tex check`)
- [x] First-run onboarding with Rich progress for Docker image pull
- [x] Welcome screen with guided workflow and "Initialise project here" button
- [x] `mark2tex init` — scaffold a template into the current directory
- [x] Auto-inject YAML frontmatter for files without it (with backup & restore)
- [x] Directory tree traversal in the file panel (subdirs + `../` navigation)
- [x] Frontmatter validator — missing fields, placeholders, template mismatch, lang validation
- [x] Template swap — preserve user values when switching templates in the TUI
- [x] Incremental latexmk builds with OS-standard user cache
- [x] Compile timeout with `MARK2TEX_TIMEOUT` override
- [x] Exclusive compilation worker (cancel-and-restart)
- [x] `mark2tex clean` — wipe latexmk build cache
- [x] Watch Mode race-condition fix (abort stale container before new Pandoc run)
- [ ] Additional ABNT templates (dissertation, presentation)

See open [issues](https://github.com/Hylbert/Mark2TeX/issues) to follow along or suggest features.

## Troubleshooting

### macOS: Docker socket not found (`Connection aborted. FileNotFoundError`)

If you see an error like this after installing via `pipx` on macOS:

```
❌  Erro ao acessar o Docker: Error while fetching server API version:
('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

This happens because Docker Desktop on macOS places its Unix socket at
`~/.docker/run/docker.sock` instead of the Linux default `/var/run/docker.sock`
that the Python Docker client tries first.

**Fix — set `DOCKER_HOST` permanently in your shell:**

```bash
# Confirm the socket exists (Docker Desktop must be running)
ls ~/.docker/run/docker.sock

# Add the variable to your shell profile
echo 'export DOCKER_HOST=unix://$HOME/.docker/run/docker.sock' >> ~/.zshrc
source ~/.zshrc

# Verify
mark2tex check
```

> **Using Colima instead of Docker Desktop?** The socket path is different:
> ```bash
> echo 'export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock' >> ~/.zshrc
> source ~/.zshrc
> ```

> **Socket not at `~/.docker/run/`?** Locate it with:
> ```bash
> find ~ -name "docker.sock" 2>/dev/null
> ```
> Then use the found path in `DOCKER_HOST`.

## Contributing

Mark2TeX grows with the help of the community. All skill levels are welcome — from fixing typos to designing new templates.

1. Read the [Contributing Guide](.github/CONTRIBUTING.md).
2. Read the [Code of Conduct](.github/CODE_OF_CONDUCT.md).
3. Open an issue before large changes so we can discuss direction.
4. Fork, branch, implement, and open a pull request.

We are grateful for every contribution. ✨

## License

Mark2TeX is released under the [MIT License](LICENSE).

---

## Star History

<a href="https://star-history.com/#Hylbert/Mark2TeX&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Hylbert/Mark2TeX&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Hylbert/Mark2TeX&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Hylbert/Mark2TeX&type=Date" />
  </picture>
</a>

---
<div align="center">
  Built by <a href="https://github.com/Hylbert">Hylbert</a> and <a href="https://github.com/Hylbert/Mark2TeX/graphs/contributors">contributors</a>.
</div>
