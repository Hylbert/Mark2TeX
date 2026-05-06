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
</div>

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

```bash
# 1 — install (requires Python 3.10+ and Docker)
pipx install mark2tex

# 2 — check your environment (recommended on first install)
mark2tex check

# 3 — open the TUI dashboard (Docker image is pulled automatically)
mark2tex
```

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
| `mark2tex uninstall` | Remove the Mark2TeX Docker image and assets |
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
  <img src="assets/dashboard_v2_m2t.png" alt="Mark2TeX Dashboard" width="800">
</p>

1. Select a `.md` file from the left panel.
2. Choose a template (`tcc-abnt`, `artigo-ieee`, `doc-tecnica`, `projeto`).
3. Optionally pick a font (`Liberation Serif`, `Liberation Sans`, `Nimbus Sans`, `Ubuntu`).
4. Press **`c`** to compile or **`w`** to toggle Watch Mode.

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
- **Watch mode** — automatic recompilation on every file save.
- **Human-readable logs** — raw XeLaTeX output is parsed and translated into plain-language messages.
- **Font selection** — choose between Liberation Sans (Arial-compatible), Nimbus Sans (Helvetica), Liberation Serif (Times-compatible), and Ubuntu per document.
- **Bibliography support** — BibTeX via Pandoc + XeLaTeX; just drop a `referencias.bib` alongside your `.md`.
- **System health check** — `mark2tex check` diagnoses your environment before you compile.
- **Rich image pull progress** — per-layer progress bars with speed and ETA when pulling the Docker image on first run.
- **YAML frontmatter injection** — files without a YAML header are highlighted in amber in the TUI; a confirmation modal injects the frontmatter automatically before compilation. A backup is saved to `~/.local/share/mark2tex/backups/` and can be restored at any time with `mark2tex restore <file>`.
- **ABNT-oriented workflow** — templates built around Brazilian academic standards.

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
- [ ] Additional ABNT templates (dissertation, presentation)
- [ ] Windows-native installer
- [ ] GitHub Actions integration for CI PDF generation

See open [issues](https://github.com/Hylbert/Mark2TeX/issues) to follow along or suggest features.

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
<div align="center">
  Built with ❤︎ by <a href="https://github.com/Hylbert">Hylbert</a> and <a href="https://github.com/Hylbert/Mark2TeX/graphs/contributors">contributors</a>.
</div>
