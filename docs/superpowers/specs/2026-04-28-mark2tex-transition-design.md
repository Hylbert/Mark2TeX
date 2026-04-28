# Design Specification: Transition from LateXOS to Mark2TeX

**Date:** 2026-04-28
**Status:** Draft
**Topic:** Project Renaming, Restructuring, and Governance Establishment

## 1. Overview
This document outlines the transition of the project from `LateXOS` to `Mark2TeX`. The goal is to rename the project to better reflect its purpose, restructure the directory layout for professional distribution, and establish strict development governance.

## 2. Renaming and Restructuring

### 2.1 Global Renaming
All occurrences of the string `LateXOS` (case-insensitive where appropriate) will be replaced with `Mark2TeX` across:
- Folder names
- File names
- Variable names in `Makefile`
- Code comments and documentation
- Docker image labels/names

### 2.2 Directory Layout (Professional Structure)
The project will be reorganized from a flat/mixed structure to a functional hierarchy:

| Current Path | Target Path | Purpose |
| :--- | :--- | :--- |
| `scripts/build.sh` | `bin/build.sh` | Core compilation logic |
| `watch.sh` | `bin/watch.sh` | File watcher script |
| `templates/` | `templates/` | LaTeX templates (preserved internal structure) |
| `template_*.md` | `examples/*.md` | Markdown boilerplates for users |
| `LateXOS_Manual_Teste.md` | `docs/manual.md` | Detailed technical documentation |
| `Dockerfile` | `Dockerfile` | Environment definition (Root) |
| `Makefile` | `Makefile` | User interface / Command entry (Root) |
| (New) | `README.md` | Quick-start guide and project overview |
| (New) | `.gitignore` | Filter for TeX build artifacts and PDFs |
| (New) | `docs/` | General project documentation folder |

## 3. Governance and Standards

### 3.1 Branching Model (GitFlow)
- `main`: Production-ready, stable, and tagged releases.
- `develop`: Integration branch for features.
- `feature/*`: For new functionality (merges into `develop`).
- `hotfix/*`: For critical production bugs (merges into `main` and `develop`).

### 3.2 Commit Standards (Conventional Commits in Portuguese)
Format: `<tipo>(escopo): <descrição>`
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Alterações em documentação
- `style`: Formatação, renomeação, estilo (sem alteração de lógica)
- `refactor`: Refatoração de código
- `chore`: Tarefas de manutenção, dependências, build

### 3.3 Versioning (Semantic Versioning 2.0.0)
Format: `MAJOR.MINOR.PATCH`
- **MAJOR**: Mudanças incompatíveis (Breaking changes).
- **MINOR**: Novas funcionalidades retrocompatíveis.
- **PATCH**: Correções de bugs retrocompatíveis.

### 3.4 Documentation Policy
- **Definition of Done**: A feature is only complete when its corresponding documentation in `docs/` or `README.md` is updated.
- **Hierarchy**: `README.md` (Quick Start) $\rightarrow$ `docs/manual.md` (Deep Dive).

## 4. Success Criteria
- All `LateXOS` references are removed.
- The project compiles successfully from the new structure.
- Git repository is initialized with `main` and `develop` branches.
- Documentation is consistent with the new layout.
