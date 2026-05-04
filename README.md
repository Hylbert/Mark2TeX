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
pipx install -e .

# 2 — build the Docker image (first run only)
make build

# 3 — open the TUI inside your project folder
mark2tex
```

> **Important:** `make build` must be run at least once before the first compilation. It builds the `mark2tex:latest` Docker image that contains XeLaTeX, Pandoc, and all required fonts. Subsequent runs reuse the cached image unless the `Dockerfile` changes.

## TUI at a Glance

<p align="center">
  <img src="assets/dashboard_v2_m2t.png" alt="Mark2TeX Dashboard" width="800">
</p>

1. Select a `.md` file from the left panel.
2. Choose a template (`tcc`, `artigo-ieee`, `doc-tecnica`, `projeto`, `apresentacao`).
3. Optionally pick a font (`--font arial | helvetica | times | ubuntu`).
4. Press **`c`** to compile or **`w`** to toggle Watch Mode.

### Keyboard shortcuts

| Key | Action |
|---|---|
| `c` | Compile |
| `w` | Toggle Watch Mode |
| `F1` / `?` | Help |
| `Esc` / `q` | Global menu |

## Features

- **Dockerized builds** — zero local LaTeX installation; identical output on every machine.
- **Interactive TUI** — file browser, template selector, real-time log console, and progress bar built with [Textual](https://github.com/Textualize/textual).
- **Watch mode** — automatic recompilation on every file save.
- **Human-readable logs** — raw XeLaTeX output is parsed and translated into plain-language messages.
- **Font selection** — choose between Liberation Sans (Arial-compatible), Nimbus Sans (Helvetica), Liberation Serif (Times-compatible), and Ubuntu per document.
- **Bibliography support** — BibTeX via Pandoc + XeLaTeX; just drop a `referencias.bib` alongside your `.md`.
- **ABNT-oriented workflow** — templates built around Brazilian academic standards.

## Available Templates

| Template | Purpose |
|---|---|
| `tcc` | Undergraduate thesis (ABNT) |
| `artigo-ieee` | IEEE conference paper |
| `doc-tecnica` | Technical documentation |
| `projeto` | Project proposal |
| `apresentacao` | Beamer-based presentation |

## Roadmap

- [ ] Additional ABNT templates (article, dissertation)
- [ ] GUI font and template preview
- [ ] `mark2tex new <template>` scaffold command
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
