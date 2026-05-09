---
title: Mark2TeX Operation Manual and Reference Guide
author: Your Name
institution: Academic Automation Ecosystem
campus: Virtual Campus
department: Tool Development
course: Software Engineering
advisor: Automation
coadvisor: Productivity
city: Digital World
year: "2026"
acknowledgments: We thank all students who seek to simplify the formatting of their academic work.
abstract-pt: Este documento serve como manual de usuário e prova de conceito para a ferramenta Mark2TeX. Ele demonstra a capacidade de conversão de Markdown para PDF seguindo as normas ABNT, validando a instalação do ambiente Docker e do motor XeLaTeX.
abstract-en: This document serves as a user manual and proof of concept for the Mark2TeX tool. It demonstrates the ability to convert Markdown to PDF following ABNT standards, validating the Docker environment and XeLaTeX engine installation.
siglas: \begin{description} \item[ABNT] Associação Brasileira de Normas Técnicas \item[PDF] Portable Document Format \item[YAML] Yet Another Markup Language \item[TCC] Trabalho de Conclusão de Curso \end{description}
simbolos: \begin{description} \item[$\rightarrow$] Flow direction \item[$\sum$] Summation of elements \item[$\alpha$] Learning coefficient \end{description}
bibliography: references.bib
---

# Introduction to Mark2TeX

**Mark2TeX** is an academic document automation system that decouples content from formatting. Instead of wrestling with complex LaTeX syntax, the user writes in **Markdown**, and the tool handles all the ABNT standard bureaucracy through a Dockerized pipeline.

## The Workflow
The process follows this chain:
**Markdown** $\rightarrow$ **Pandoc** $\rightarrow$ **XeLaTeX** $\rightarrow$ **PDF**

This ensures that anyone with Docker installed can generate the same PDF, without needing to install gigabytes of TeX distributions locally.

# Operation Guide (Commands)

Mark2TeX offers two modes of operation: through an Interactive Dashboard (TUI) or via the command line (CLI).

## 🖥️ Dashboard Operation (Recommended)

The Dashboard is the most intuitive way to use the tool. To start it, run:
`mark2tex`

### Dashboard features:
1. **File Explorer**: In the left panel, navigate and select the `.md` file you want to compile.
2. **Template Selection**: In the centre panel, choose from the available templates (`tcc`, `artigo` or `projeto`).
3. **Compilation**: Press `c` or click **🚀 COMPILE**. Progress will be displayed in real time in the status bar and the bottom console.
4. **Watch Mode (Auto-compile)**: Press `w` or click **👀 WATCH**. The tool will monitor the selected file and trigger compilation automatically on every save.
5. **Help and Menus**: Press `F1` or `?` to see shortcuts, and `ESC` or `q` to access the global menu.

---

## ⌨️ Terminal Operation (CLI)

For users who prefer automation or scripts, the command-line interface remains available.

### Preparing the environment
If this is the first time using the tool or if the `Dockerfile` has been changed:
`make build-image`

### Generating the PDF (manual)
To compile a specific file:
`make compile INPUT=filename.md TEMPLATE=tcc`

*   **INPUT**: The Markdown file containing your text.
*   **TEMPLATE**: The template to use (e.g. `tcc`).

# Anatomy of the Markdown File

The secret of Mark2TeX lies in the **YAML** header, located at the top of the file between two sets of `---`.

## Main Fields
- `title`: Work title (appears on the cover and title page).
- `author`: Your full name.
- `institution`/`campus`/`department`: Institutional data for the cover header.
- `siglas`: List of abbreviations using the LaTeX `description` environment.
- `simbolos`: List of mathematical symbols.

**Important tip**: Always use single quotes (`' '`) when wrapping LaTeX commands in YAML to avoid escape errors.

# Resource Gallery (Demonstration)

This section proves that the tool is working correctly.

## Mathematics and Formulas
Mark2TeX supports full mathematics. We can have inline formulas such as $E = mc^2$ or block formulas:

$$
\int_{a}^{b} f(x) \,dx = F(b) - F(a)
$$

## Code and Programming
Code blocks are formatted with monospaced fonts and syntax highlighting. Example in Python:

```python
def greeting(name):
    print(f"Hello, {name}! Welcome to Mark2TeX.")

greeting("User")
```

## Text Formatting
- **Bold** for emphasis.
- *Italic* for foreign terms.
- Bullet lists:
    - Item A
    - Item B
- Numbered lists:
    1. First step
    2. Second step

## Citations and Bibliography
Citations are made via BibTeX. By using the `\cite{key}` command, the system looks up the reference in the `.bib` file and automatically generates the final list following ABNT standards.

# Test Conclusions

If you are reading this PDF, it means that:

1. Docker is correctly configured.
2. The Times New Roman fonts were installed.
3. The XeLaTeX engine is processing Markdown via Pandoc.
4. The ABNT standard is being applied.

All set to start your thesis!
