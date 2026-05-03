# Contributing to Mark2TeX

**⚠️ Project Status: BETA**
Mark2TeX is currently in Beta. We are welcoming community contributions, but please be aware that the architecture and interface may undergo significant structural changes as we refine the tool.

We are thrilled that you are interested in contributing to Mark2TeX! 🚀 Before submitting your contribution, please take a moment to read these guidelines.

- [Philosophy](#philosophy)
- [Issue Reporting Guidelines](#issue-reporting-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Where to Start?](#where-to-start)
- [Quick Start](#quick-start)

## Philosophy

🔑 Our philosophy is to keep things clean, simple, and minimalist.
Mark2TeX aims to remove the friction between the idea and the final document. We want improvements to align with this simplicity: the tool should be powerful under the hood, but invisible and intuitive for the user.

## Issue Reporting Guidelines

Please search for similar issues before opening a new one and always use the available issue template. If you find a bug or have a feature suggestion, describe the scenario in detail, the Docker version used, and if possible, attach an example of the Markdown file that caused the problem.

## Pull Request Guidelines

**For *all* Pull Requests**: provide a detailed description of the problem solved or the feature added.

Before submitting your PR, make sure that:

- The PR is submitted directly to the `develop` branch.
- The final merge must be performed using the `--no-ff` flag to preserve the branch history.
- **Language**: All commit messages and Pull Request descriptions must be written in **English**, following the [Conventional Commits](https://www.conventionalcommits.org/) standard.
- You referenced the related issue in the PR comment.
- The documentation in `docs/` or `README.md` has been updated to reflect the change.
- All compilation tests pass (the PDF is generated without errors).
- The code follows programming best practices and is clean.

### If you are adding a new feature:

- Open an issue for suggestion first so we can discuss the implementation.
- Provide the justification for why this feature is useful for the user.
- Submit your PR after agreement from the maintainers.

### If you are fixing a bug:

- If you are resolving a specific issue, add `fix: #<issue-number> <short message>` to your PR title (e.g., `fix: #12 fixes character encoding error`).
- Provide a detailed description of the bug and how the fix resolves it.

## Where to Start?

A great way to start is by looking for issues with the `bug`, `help wanted`, or `feature request` labels. Issues marked as `good first issue` are ideal for new contributors.

For larger changes, discuss the solution first; for small changes, you can open the PR directly.

## Quick Start

1. **Fork** the repository.
2. Clone your fork: `git clone git@github.com:<your-username>/Mark2TeX.git`
3. Create a feature branch: `git checkout -b feature/feature-name`
4. Implement the changes and push your branch.
5. Create a Pull Request against the `develop` branch describing your changes.

**Syncing your PR:**

If there are conflicts or if you want to update your local branch:
1. `git fetch upstream`
2. `git rebase upstream/develop`
3. Resolve conflicts and force push: `git push -f`

---

Thank you for your time and effort in making Mark2TeX better for everyone! 🎓