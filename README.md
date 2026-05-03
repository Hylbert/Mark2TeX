<p align="center">
  <img src="assets/logo.png" alt="Mark2TeX" width="150" height="150">
</p>

<h1 align="center">Mark2TeX</h1>

<div align="center">
  <strong><span style="color: #03656b;">English</span> | <a href="README.pt-BR.md">Português (Brasil)</a></strong>
</div>

<div align="center">
  <strong>🚀 Academic Markdown to PDF with ABNT, Docker and interactive TUI 🎓</strong><br>
  A tool for writing in Markdown and compiling academic documents with LaTeX templates through a terminal interface and a Dockerized pipeline.
</div>

<br>

<div align="center">
  <img src="https://img.shields.io/badge/workflow-GitFlow-orange.svg" alt="GitFlow">
  <img src="https://img.shields.io/badge/version-SemVer-green.svg" alt="SemVer">
</div>

<div align="center">
  <h3>
    <a href="#features">
      ✨ Features
    </a>
    <span> | </span>
    <a href="#installation">
      🚀 Installation
    </a>
    <span> | </span>
    <a href="#project-structure">
      📂 Structure
    </a>
    <span> | </span>
    <a href=".github/CONTRIBUTING.md">
      🤝 Contribution
    </a>
  </h3>
</div>

<div align="center">
  <sub>Built with ❤︎ by <a href="https://github.com/Hylbert">Hylbert</a> and contributors.</sub>
</div>

<br />

## ✨ Overview

Mark2TeX separates writing from formatting: the content stays in Markdown, while the final rendering is performed by Pandoc, XeLaTeX, and LaTeX templates inside a Docker container. The current version includes a TUI (Terminal User Interface) developed with Textual, offering file selection, template choice, real-time compilation console, watch mode, and keyboard shortcuts. 🖥️

## 🚀 Features

- **🎓 ABNT Compilation**: Generation of PDFs using academic templates (`tcc`, `article`, `project`).
- **📦 Isolated Execution**: Docker pipeline, eliminating the need to install massive TeX distributions locally.
- **🎨 TUI Interface**: Interactive dashboard with Markdown file list, progress bar, and log console.
- **🔭 Integrated Watch Mode**: Automatic recompilation of the selected file whenever it is saved.
- **🔍 Smart Logs**: Translation and filtering of LaTeX logs to make error messages more readable.
- **📚 Automatic Bibliography**: BibTeX support via `Pandoc` and `XeLaTeX`.

## 🛠️ Requirements

Before using Mark2TeX, make sure you have installed:

- **🐍 Python 3.10** or higher.
- **🐳 Docker** installed and daemon running.
- **📦 pipx** (recommended) for global command installation in an isolated environment.

## 🚀 Installation

### 🛠️ Installation with pipx (Recommended)

![platform](https://img.shields.io/static/v1.svg?label=Platform&message=Docker%20(Linux%20|%20macOS%20|%20Windows)&style=for-the-badge)

In the project directory, run:

```bash
pipx install -e .
```

This command installs the application in editable mode within an isolated virtual environment. Docker validation and the creation of the `mark2tex:latest` image happen automatically when starting the main command.

### 🛠️ Updating after code changes

If you changed dependencies, entry points, or package metadata, update the installation with:

```bash
pipx reinstall -e .
```

## First Use

Go to a folder containing `.md` files and run:

```bash
mark2tex
```

Upon startup, the application verifies Docker connectivity and ensures the availability of the compilation image. The TUI will list the Markdown files in the current directory so you can start your project.

## 🎮 TUI Usage

### Basic Flow

1. Start the app with `mark2tex` inside your project folder.
2. Select the desired `.md` file from the list on the left.
3. Choose a template (`tcc`, `article`, or `project`).
4. Press `c` or click the **COMPILE** button.
5. Follow the progress and messages in the bottom console.

<p align="center">
  <img src="assets/dashboard_v2_m2t.png" alt="Mark2TeX Dashboard" width="800">
</p>

### Keyboard Shortcuts

- `c`: Compile document.
- `w`: Toggle Watch Mode.
- `F1` or `?`: Open Help menu.
- `Esc` or `q`: Open Global Menu.

<p align="center">
  <img src="assets/atalhos_v2_m2t.png" alt="Mark2TeX Keyboard Shortcuts" width="400">
</p>

### Watch Mode

The Watch Mode is controlled internally by the TUI. When activated, it monitors the selected file and triggers automatic recompilation via callback as soon as changes are detected on disk.

<p align="center">
  <img src="assets/modo_watch_v2_m2t.png" alt="Mark2TeX Watch Mode" width="800">
</p>

## Command Line and Legacy Scripts

Although the primary flow is now centered on the `mark2tex` command and the TUI, legacy scripts and `make` commands remain available for compatibility and external automation:

```bash
make compile INPUT=my_work.md TEMPLATE=tcc
```

This mode is useful for quick tests or integration with other CI/CD tools.

## 📂 Project Structure

- `src/app.py`: TUI Interface built with Textual.
- `src/cli.py`: Main entry point for the `mark2tex` command.
- `src/setup_env.py`: Environment check and Docker image management.
- `src/docker_manager.py`: Orchestration of the build pipeline inside the container.
- `src/watcher.py`: Integrated Watch Mode logic.
- `src/log_translator.py`: Cleaning and partial translation of compilation logs.
- `bin/build.sh`: Core compilation script executed inside the container.
- `templates/`: Parameterized LaTeX templates.

## Development

For local development, use the following flow:

```bash
pipx install -e .
mark2tex
```

To remove the installation: `pipx uninstall mark2tex`. The `mark2tex uninstall` command can also be used to clear project Docker artifacts.

## 🤝 Contribution

Mark2TeX is an open-source project and grows with the help of the community. If you wish to add new templates or improve the pipeline, please read our [Contribution Guide](.github/CONTRIBUTING.md) and our [Code of Conduct](.github/CODE_OF_CONDUCT.md).

---
<div align="center">
  Developed to simplify the lives of students and researchers. 🎓
</div>
