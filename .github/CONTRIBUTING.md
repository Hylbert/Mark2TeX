# Contributing to Mark2TeX

Thank you for taking the time to contribute! Mark2TeX is built in the open and every contribution — from fixing a typo to adding a full template — makes a real difference.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Branch Strategy](#branch-strategy)
4. [Commit Messages](#commit-messages)
5. [Pull Request Process](#pull-request-process)
6. [Running Locally](#running-locally)
7. [Project Structure](#project-structure)

---

## Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/Mark2TeX.git
   cd Mark2TeX
   ```
3. **Create a branch** from `develop` (see [Branch Strategy](#branch-strategy)).
4. **Make your changes**, following the coding style already in use.
5. **Open a Pull Request** against `develop`.

---

## Branch Strategy

Mark2TeX follows **GitFlow**:

| Branch | Purpose |
|---|---|
| `main` | Stable production releases only |
| `develop` | Integration branch — all PRs target here |
| `feature/<slug>` | New features and non-urgent improvements |
| `fix/<slug>` | Bug fixes |
| `hotfix/<slug>` | Critical fixes branched directly from `main` |
| `docs/<slug>` | Documentation-only changes |
| `release/<version>` | Release preparation |

**Rules:**
- Always branch from `develop` (except hotfixes, which branch from `main`).
- Never commit directly to `main` or `develop`.
- Keep branches focused — one feature or fix per branch.
- Delete branches after merging.

---

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:**

| Type | When to use |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation changes only |
| `style` | Formatting, missing semicolons — no logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or correcting tests |
| `chore` | Build process, tooling, dependencies |

**Examples:**
```
feat(templates): add ABNT article template
fix(build.sh): normalize CRLF line endings
docs(readme): update quickstart with make build step
```

---

## Pull Request Process

1. Ensure your branch is up to date with `develop`:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```
2. Fill out the [PR template](PULL_REQUEST_TEMPLATE.md) completely.
3. Link any related issues in the PR description using `Closes #<issue>`.
4. A maintainer will review the PR. Address any requested changes.
5. Once approved, the maintainer will merge using squash-merge to keep `develop` history clean.

---

## Running Locally

### Requirements

- Python 3.10+
- Docker (daemon running)
- `pipx`
- `make`

### Setup

```bash
# Install in editable mode
pipx install -e .

# Build the Docker image (required before first compilation)
make build
```

> **Why `make build`?** The `make build` command constructs the `mark2tex:latest` Docker image containing XeLaTeX, Pandoc, and all required fonts. Without it, the compilation pipeline has nothing to run inside. After the initial build, Docker caches the image — you only need to rebuild when the `Dockerfile` changes.

### Running the TUI

```bash
# Navigate to a folder with .md files
cd path/to/your/project
mark2tex
```

### Running tests

```bash
make test
```

### Resetting the environment

```bash
pipx uninstall mark2tex
# or, to also remove Docker artifacts:
mark2tex uninstall
```

---

## Project Structure

```
Mark2TeX/
├── src/
│   ├── app.py            # TUI interface (Textual)
│   ├── cli.py            # Entry point for `mark2tex` command
│   ├── setup_env.py      # Docker environment check
│   ├── docker_manager.py # Build pipeline orchestration
│   ├── watcher.py        # Watch mode logic
│   └── log_translator.py # LaTeX log parsing and translation
├── bin/
│   └── build.sh          # Core compilation script (runs inside Docker)
├── templates/            # LaTeX templates (one subdirectory per template)
├── examples/             # Example .md files for each template
├── docs/                 # Extended documentation
├── Dockerfile            # Docker image definition
├── Makefile              # Helper targets: build, compile, test
└── pyproject.toml        # Python package metadata
```
