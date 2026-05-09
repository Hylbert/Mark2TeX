# User Guide — Mark2TeX

> **About this document**
> The README covers installation, quickstart, and an overview.
> This guide covers advanced usage: detailed configuration for each template,
> Watch Mode, XeLaTeX error resolution, and CI pipeline integration.

## Table of Contents

1. [Installation — `pipx` and full uninstall](#1-installation--pipx-and-full-uninstall)
2. [How Mark2TeX works internally](#2-how-mark2tex-works-internally)
3. [The Markdown file — complete YAML reference](#3-the-markdown-file--complete-yaml-reference)
4. [Templates — per-template guide](#4-templates--per-template-guide)
5. [Fonts — when to use each one](#5-fonts--when-to-use-each-one)
6. [BibTeX — bibliography step by step](#6-bibtex--bibliography-step-by-step)
7. [Watch Mode — how it works](#7-watch-mode--how-it-works)
8. [Docker internals — what's in the image](#8-docker-internals--whats-in-the-image)
9. [System health check (`mark2tex check`)](#9-system-health-check-mark2tex-check)
10. [Common XeLaTeX errors — what they mean](#10-common-xelatex-errors--what-they-mean)
11. [CI/CD integration](#11-cicd-integration)

---

## 1. Installation — `pipx` and full uninstall

### 1.1 Why `pipx`?

Mark2TeX is a command-line tool, not a library.
`pipx` is the recommended method for installing Python CLI tools because:

- Automatically creates an isolated virtual environment for each tool
- Does not pollute the system Python or interfere with other projects
- Makes the `mark2tex` command globally available without a manual `venv`
- Simplifies upgrades (`pipx upgrade mark2tex`) and clean removal

### 1.2 Installing `pipx`

```bash
# Ubuntu / Debian
sudo apt install pipx && pipx ensurepath

# macOS
brew install pipx && pipx ensurepath

# Windows (PowerShell)
python -m pip install --user pipx
python -m pipx ensurepath
```

> Restart your terminal after running `ensurepath` so the PATH is updated.

### 1.3 Installing Mark2TeX

```bash
pipx install mark2tex
```

Verify the installation:

```bash
mark2tex check
```

### 1.4 Upgrading

```bash
pipx upgrade mark2tex
```

### 1.5 Full uninstall

Uninstallation **must follow this order**:

**Step 1 — clean data and Docker images:**

```bash
mark2tex uninstall
```

This command removes:
- The Docker images `hylbert/mark2tex:latest` and `mark2tex:latest`
- The user data directory (`~/.local/share/mark2tex/`), including YAML backups
- The user configuration directory (`~/.config/mark2tex/`)

**Step 2 — remove the Python package:**

```bash
pipx uninstall mark2tex
```

> ⚠️ **Do not skip Step 1.** Running `pipx uninstall mark2tex` without first running
> `mark2tex uninstall` leaves Docker images (~1.1 GB) and user data
> on disk with no way to remove them through Mark2TeX.

---

## 2. How Mark2TeX works internally

Understanding the pipeline avoids surprises when something goes wrong.

```
┌─────────────────────────────────────────────────────────────────┐
│  Host (your machine)                                            │
│                                                                 │
│  file.md ──► mark2tex CLI ──► docker run mark2tex:latest        │
│                  │                        │                     │
│                  │            ┌───────────▼──────────────┐      │
│                  │            │  Container               │      │
│                  │            │  pandoc → file.tex       │      │
│                  │            │  xelatex (2×) → .pdf     │      │
│                  │            │  biber (if .bib) → .bbl  │      │
│                  └────────────►  output copied back       │      │
│                               └──────────────────────────┘      │
│  file.pdf ◄── same directory as the .md                         │
└─────────────────────────────────────────────────────────────────┘
```

**Why does XeLaTeX run twice?**
The first pass generates internal references (section numbering, figures,
tables). The second resolves those references in the final document. With
a bibliography, a Biber pass is interleaved between the two.

**Where is the PDF generated?**
Always in the same directory as the source `.md` file. Intermediate files
(`.aux`, `.log`, `.toc`) are discarded inside the container; only the final
`.pdf` is copied back to the host.

---

## 3. The Markdown file — complete YAML reference

The YAML header controls metadata, cover page, table of contents, standard, and compilation.
It must be placed between `---` at the very beginning of the file, before any content.

### 3.1 Universal fields (all templates)

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | string | — | Main title; appears on the cover and in PDF metadata |
| `author` | string | — | Author's full name |
| `date` | string | current date | Submission date (`YYYY-MM-DD` or free text) |
| `lang` | string | `pt-BR` | Language; affects hyphenation and automatic labels |
| `bibliography` | string | — | Relative path to the `.bib` file (e.g. `references.bib`) |
| `font` | string | `liberation-serif` | Typeface (see [section 5](#5-fonts--when-to-use-each-one)) |

> **Tip:** Wrap values containing LaTeX special characters in single quotes:
> ```yaml
> title: 'Analysis of $\alpha$-ketoacids in clinical samples'
> ```

### 3.2 Template-specific fields — `tcc-abnt`

| Field | Required | Description |
|---|---|---|
| `institution` | Yes | Institution name (cover page) |
| `campus` | No | Campus or unit |
| `department` | No | Department or programme |
| `course` | No | Course name |
| `advisor` | Yes | Advisor's name |
| `coadvisor` | No | Co-advisor's name |
| `city` | Yes | City (cover page and title page) |
| `year` | Yes | Defence year (in quotes: `"2026"`) |
| `abstract-pt` | Yes | Abstract in Portuguese (continuous text, no line breaks) |
| `abstract-en` | Yes | Abstract in English |
| `acknowledgments` | No | Acknowledgements (continuous text) |
| `siglas` | No | List of abbreviations in LaTeX (see example below) |
| `simbolos` | No | List of mathematical symbols in LaTeX |

**Full `tcc-abnt` example:**

```yaml
---
title: "Title of the Final Course Work"
author: "Author Full Name"
date: "2026-01-01"
institution: Name of the Institution
campus: Campus Name
department: Department Name
course: Course Name
advisor: Prof. Dr. Advisor Name
coadvisor: Prof. Me. Co-advisor Name
city: City
year: "2026"
lang: pt-BR
abstract-pt: 'Write the abstract in Portuguese here...'
abstract-en: 'Write the abstract in English here...'
acknowledgments: 'Write the acknowledgements here...'
siglas: \begin{description}
  \item[ABNT] Associação Brasileira de Normas Técnicas
  \item[PDF]  Portable Document Format
  \end{description}
bibliography: references.bib
font: liberation-serif
---
```

### 3.3 Template-specific fields — `artigo-ieee`

| Field | Required | Description |
|---|---|---|
| `abstract` | Yes | Article abstract (single field, IEEE standard) |
| `keywords` | No | Comma-separated keywords |

### 3.4 Template-specific fields — `artigo-abnt`

Same fields as `tcc-abnt`, with `abstract-pt` and `abstract-en`, plus:

| Field | Required | Description |
|---|---|---|
| `journal` | No | Target journal name |
| `keywords-pt` | No | Keywords in Portuguese |
| `keywords-en` | No | Keywords in English |

### 3.5 Template-specific fields — `doc-tecnica` and `projeto`

| Field | Required | Description |
|---|---|---|
| `version` | No | Document version (e.g. `"1.0.0"`) |
| `status` | No | Status (`Draft`, `Approved`, `Under review`) |
| `team` | No | Responsible team or department |

---

## 4. Templates — per-template guide

### `tcc-abnt`

Produces a complete final course work following ABNT NBR 14724. Automatically includes:
cover page, title page, blank approval sheet, abstract (PT and EN),
list of abbreviations/symbols, table of contents, body text, and references.

**Recommended directory structure:**

```
project/
├── my-thesis.md
├── references.bib
└── figures/
    └── diagram.png
```

**Inserting figures:**

```markdown
![Figure caption](figures/diagram.png){width=80%}
```

The path is relative to the `.md` file. Width accepts `%` (relative to the text column)
or `cm`.

---

### `artigo-ieee`

Produces a standard IEEE two-column layout. Does not include a table of contents.
References follow the IEEE numeric style.

> **Note on the `lang` field:** Babel (LaTeX language package) **does not accept
> BCP-47 codes** such as `en-US` or `pt-BR`. For `artigo-ieee`, always use the
> Babel-recognised language name:
>
> | Language | Correct value for `lang` |
> |---|---|
> | English | `english` |
> | Brazilian Portuguese | `brazil` |
> | Spanish | `spanish` |
>
> The default value injected by Mark2TeX for this template is `"english"`.
> Using a BCP-47 code will cause XeLaTeX to emit a fatal error
> `Unknown option '<code>'` and the compilation will fail.

**In-text citation:**

```markdown
As demonstrated in \cite{liu2020isolation}, the algorithm...
```

**Full-width figures (two columns):**

Wide figures require the LaTeX `figure*` environment.
Use a raw block for this:

````markdown
```{=latex}
\begin{figure*}[ht]
  \centering
  \includegraphics[width=\textwidth]{figures/result.png}
  \caption{Overall experiment result.}
\end{figure*}
```
````

---

### `artigo-abnt`

Single-column layout. Citations follow ABNT NBR 6023 (author-date).

**In-text citation:**

```markdown
# Simple citation
Anomaly detection \cite{liu2020isolation} has been widely...

# With page number
According to (LIU, 2020, p. 42), the method...
```

---

### `doc-tecnica`

Suitable for internal READMEs, specifications, and deployment guides.
Does not require full cover fields — `title`, `author`, and `date` are sufficient.
Includes a header with version number and document status.

---

### `projeto`

Suitable for project proposals, work plans, and schedules.
Natively supports schedule tables in Markdown.

---

## 5. Fonts — when to use each one

Mark2TeX uses fonts that are metrically compatible with those required by academic
standards, freely distributed under open-source licences.

| `font` value | Actual family | Compatible with | Recommended for |
|---|---|---|---|
| `liberation-serif` | Liberation Serif | Times New Roman | Thesis, ABNT articles (default) |
| `liberation-sans` | Liberation Sans | Arial | Presentations, doc-tecnica |
| `nimbus-sans` | Nimbus Sans | Helvetica | IEEE articles, international publications |
| `ubuntu` | Ubuntu | — | Technical documentation, digital projects |

**How to specify in YAML:**

```yaml
font: nimbus-sans
```

> **ABNT note:** NBR 14724 requires "Arial or Times New Roman, size 12".
> Use `liberation-sans` (Arial) or `liberation-serif` (Times) for compliance.

---

## 6. BibTeX — bibliography step by step

### 6.1 Creating the `.bib` file

Create `references.bib` in the same directory as your `.md`:

```bibtex
@article{liu2020isolation,
  author  = {Liu, Fei Tony and Ting, Kai Ming and Zhou, Zhi-Hua},
  title   = {Isolation-Based Anomaly Detection},
  journal = {ACM Transactions on Knowledge Discovery from Data},
  year    = {2012},
  volume  = {6},
  number  = {1},
  pages   = {1--39},
  doi     = {10.1145/2133360.2133363},
}

@book{abnt2011nbr,
  author    = {{Associação Brasileira de Normas Técnicas}},
  title     = {{NBR 14724}: Information and documentation},
  year      = {2011},
  address   = {Rio de Janeiro},
  publisher = {ABNT},
}
```

**Most commonly used entry types:** `@article`, `@book`, `@inproceedings`,
`@techreport`, `@misc` (for websites, with `url` and `urldate` fields).

### 6.2 Declaring in YAML

```yaml
bibliography: references.bib
```

The path is relative to the `.md` file. If the `.bib` is in another directory:

```yaml
bibliography: ../shared/references.bib
```

### 6.3 Citing in the text

```markdown
# Simple citation
The algorithm proposed by \cite{liu2020isolation} presents...

# With page number (ABNT)
According to \citeonline{liu2020isolation} (p. 15), the isolation...

# Multiple references
Several studies \cite{liu2020isolation,abnt2011nbr} demonstrate...
```

### 6.4 Where the reference list appears

Mark2TeX automatically inserts references at the end of the document,
after the last chapter. No manual section is needed.

### 6.5 Reliable `.bib` sources

- **Google Scholar** → ❝ → BibTeX
- **IEEE Xplore** → "Cite This" button → BibTeX
- **ACM Digital Library** → Export Citation → BibTeX

> **Note:** `--bibliography` is only passed to Pandoc when the `.md` file
> contains actual citation markers (`[@key]` or `\cite{`). Documents without
> citations do not invoke Biber, avoiding the `missing \item` error loop in
> empty `.bbl` files.

---

## 7. Watch Mode — how it works

When you press `w` in the TUI (or pass `--watch` via CLI), Mark2TeX starts
a file watcher based on the [watchdog](https://github.com/gorakhargosh/watchdog) library.

**What is monitored:**

- The selected `.md` file
- The `.bib` file referenced in the YAML (if it exists)
- Image files in the same directory referenced in the `.md`

**1.5 s debounce:** multiple rapid saves trigger only
one compilation. The value is adjustable via environment variable:

```bash
MARK2TEX_WATCH_DEBOUNCE=2000 mark2tex  # 2 s debounce
```

**Incremental builds with latexmk:** Watch Mode benefits from incremental
compilations. latexmk persists intermediate files (`.aux`,
`.fdb_latexmk`, `.fls`, `.bbl`, `.xdv`) in a per-document cache directory
(`~/.cache/mark2tex/<hash>/` on Linux). On subsequent recompilations, only
the parts that changed are reprocessed, reducing time from ~18 s to ~6 s on
a 15-page document after a single-line edit. Use
`mark2tex clean [file]` to manually clear the cache if needed.

**Editors with auto-save (VS Code `formatOnSave`, JetBrains
`autosave`):** if the interval between saves is greater than 1.5 s,
each save triggers a compilation. Disable aggressive autosave
or increase the debounce as shown above.

**How to stop Watch Mode:**

- Press `w` again in the TUI
- Or `Ctrl+C` if running via CLI

---

## 8. Docker internals — what's in the image

The `mark2tex:latest` image (~1.1 GB) contains:

| Component | Version | Role |
|---|---|---|
| Ubuntu 22.04 LTS | — | Container base |
| TeX Live (selected) | 2023 | XeLaTeX engine + ABNT/IEEE packages |
| Pandoc | 3.x | Markdown → LaTeX conversion |
| Biber | 2.x | BibTeX bibliography processing |
| Liberation fonts | — | Open-source Arial/Times equivalents |
| Nimbus Sans fonts | — | Open-source Helvetica equivalent |
| Ubuntu font | — | Official Ubuntu font |

### 8.1 Manual image build

Only needed if you modified the `Dockerfile` or are offline:

```bash
# From the cloned repository root
make build-image

# Or directly
docker build -t mark2tex:latest .
```

### 8.2 Inspect what is installed

```bash
# Open an interactive shell inside the container
docker run --rm -it mark2tex:latest bash

# Inside the container:
pandoc --version
xelatex --version
biber --version
fc-list | grep -i liberation   # list available Liberation fonts
```

### 8.3 Clean the image and data

```bash
mark2tex uninstall
```

This command removes Docker images, the user data directory
(`~/.local/share/mark2tex/`) and the configuration directory (`~/.config/mark2tex/`).

> ⚠️ **Run `mark2tex uninstall` before `pipx uninstall mark2tex`.**
> Removing the package via `pipx` first makes the `mark2tex` command unavailable,
> leaving Docker images (~1.1 GB) and data on disk with no way to remove them
> through Mark2TeX. See [section 1.5](#15-full-uninstall) for the full flow.

---

## 9. System health check (`mark2tex check`)

### 9.1 What each probe checks

| Probe | Severity if failing | What it analyses |
|---|---|---|
| **Mark2TeX** | Warning | Installed version via `importlib.metadata` |
| **Docker (binary)** | ❌ Critical error | `docker` in PATH via `shutil.which` |
| **Docker (daemon)** | ❌ Critical error | `docker info` with 8 s timeout |
| **mark2tex image** | ⚠️ Warning | `docker images mark2tex:latest` via Python SDK |
| **Pandoc** | ⚠️ Warning | `pandoc` in PATH — optional, already in the image |
| **Python** | ❌ Critical error | `sys.version_info >= (3, 10)` |
| **Disk space** | ⚠️ Warning | `shutil.disk_usage(Path.home())` — threshold 2 GB |

### 9.2 Troubleshooting table

| Failed probe | Most common cause | Solution |
|---|---|---|
| Docker (binary) ❌ | Docker not installed | Install [Docker Engine](https://docs.docker.com/engine/install/) or [Docker Desktop](https://docs.docker.com/desktop/) |
| Docker (daemon) ❌ | Daemon stopped | `sudo systemctl start docker` (Linux) or open Docker Desktop |
| Docker (daemon) ❌ | User lacks permission | `sudo usermod -aG docker $USER` and reopen terminal |
| mark2tex image ⚠️ | Image not pulled | Run `mark2tex` once — the image is pulled automatically |
| mark2tex image ⚠️ | Corrupted image | `docker rmi mark2tex:latest && mark2tex` |
| Pandoc ⚠️ | Not installed on host | Ignore — Pandoc is in the Docker image |
| Python ❌ | Python < 3.10 | Install Python 3.10+ via [python.org](https://python.org) or `pyenv` |
| Disk space ⚠️ | < 2 GB free | Free up space; the image uses ~1.1 GB |

### 9.3 Using `check` in scripts and CI

```bash
# Abort if there are critical errors
mark2tex check || { echo "Invalid environment — aborting."; exit 1; }

# Silent — exit code only
mark2tex check > /dev/null 2>&1 && echo "OK" || echo "ERROR"
```

Exit code `0` when there are no errors (warnings may be present); `1` when
at least one critical probe fails.

---

## 10. Common XeLaTeX errors — what they mean

Mark2TeX translates XeLaTeX logs into plain messages, but when
compilation fails the full log appears in the TUI console. This table
helps interpret the most frequent messages.

| Log message | Cause | Solution |
|---|---|---|
| `Font ... not found` | Font declared in YAML does not exist in the image | Use one of the four valid `font` values |
| `File '....sty' not found` | LaTeX package missing from the image | Open an issue in the repository to add it to the `Dockerfile` |
| `Undefined control sequence` | Invalid LaTeX command in the `.md` body | Check raw `{=latex}` blocks for typos |
| `Missing $ inserted` | Mathematical symbol outside `$...$` | Escape the symbol (`\$`) or place it inside `$...$` |
| `Overfull \hbox` | Line too long for the column | Non-critical warning — PDF is generated anyway |
| `I can't find file` | Referenced image does not exist at the given path | Check path and file extension |
| `Citation ... undefined` | BibTeX key not found in the `.bib` | Check the key in the `.bib` and the `bibliography` field in YAML |
| `Output loop --- too many` | Cross-reference loop | Recompile — almost always resolved on the second pass |
| `Unknown option '<code>'` | BCP-47 code passed to Babel (e.g. `en-US`, `pt-BR`) | Use Babel language name: `english`, `brazil`, `spanish` |

### 10.1 Finding the root cause in the log

1. In the TUI, scroll the bottom console to the end.
2. Look for the first line starting with `!` — that is the root cause.
3. Lines starting with `l.NNN` indicate the line number in the generated
   `.tex` (useful for locating the excerpt in the original `.md`).

---

## 11. CI/CD integration

### 11.1 GitHub Actions — generate PDF on every push

Create `.github/workflows/build-pdf.yml`:

```yaml
name: Build PDF

on:
  push:
    paths:
      - 'docs/**.md'
      - 'references.bib'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Mark2TeX
        run: |
          python -m pip install --user pipx
          python -m pipx ensurepath
          pipx install mark2tex

      - name: Check environment
        run: mark2tex check

      - name: Build PDF
        run: |
          mark2tex compile docs/my-thesis.md \
            --template tcc-abnt \
            --font liberation-serif

      - name: Upload PDF
        uses: actions/upload-artifact@v4
        with:
          name: compiled-document
          path: docs/my-thesis.pdf
          retention-days: 30
```

> The `ubuntu-latest` runner already has Docker available.
> The `mark2tex check` step returns exit code `1` on critical error,
> aborting the workflow before compilation.

### 11.2 GitLab CI

```yaml
build-pdf:
  image: python:3.12-slim
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
  before_script:
    - python -m pip install --user pipx
    - python -m pipx ensurepath
    - pipx install mark2tex
    - mark2tex check
  script:
    - mark2tex compile docs/my-thesis.md --template tcc-abnt
  artifacts:
    paths:
      - docs/my-thesis.pdf
    expire_in: 1 week
```

### 11.3 Local pre-commit hook

To compile automatically before each commit:

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
set -e
echo "[mark2tex] Checking environment..."
mark2tex check || exit 1
echo "[mark2tex] Compiling documentation..."
mark2tex compile docs/my-thesis.md --template tcc-abnt
git add docs/my-thesis.pdf
```

Make the hook executable:

```bash
chmod +x .git/hooks/pre-commit
```
