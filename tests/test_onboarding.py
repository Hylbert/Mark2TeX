"""Unit tests for mark2tex.onboarding module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mark2tex.onboarding import (
    is_first_run,
    mark_onboarding_done,
    reset_onboarding,
    run_init,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _flag(tmp_path: Path) -> Path:
    return tmp_path / ".onboarding_done"


# ---------------------------------------------------------------------------
# is_first_run
# ---------------------------------------------------------------------------


def test_is_first_run_when_flag_absent(tmp_path: Path) -> None:
    with patch("mark2tex.onboarding._flag_path", return_value=_flag(tmp_path)):
        assert is_first_run() is True


def test_is_first_run_when_flag_present(tmp_path: Path) -> None:
    flag = _flag(tmp_path)
    flag.touch()
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        assert is_first_run() is False


# ---------------------------------------------------------------------------
# mark_onboarding_done
# ---------------------------------------------------------------------------


def test_mark_onboarding_done_creates_flag(tmp_path: Path) -> None:
    flag = _flag(tmp_path)
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        mark_onboarding_done()
    assert flag.exists()


def test_mark_onboarding_done_idempotent(tmp_path: Path) -> None:
    flag = _flag(tmp_path)
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        mark_onboarding_done()
        mark_onboarding_done()  # second call must not raise
    assert flag.exists()


def test_mark_onboarding_done_creates_parent_dirs(tmp_path: Path) -> None:
    flag = tmp_path / "deep" / "nested" / ".onboarding_done"
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        mark_onboarding_done()
    assert flag.exists()


# ---------------------------------------------------------------------------
# reset_onboarding
# ---------------------------------------------------------------------------


def test_reset_onboarding_removes_flag(tmp_path: Path) -> None:
    flag = _flag(tmp_path)
    flag.touch()
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        reset_onboarding()
    assert not flag.exists()


def test_reset_onboarding_noop_when_absent(tmp_path: Path) -> None:
    flag = _flag(tmp_path)
    with patch("mark2tex.onboarding._flag_path", return_value=flag):
        reset_onboarding()  # must not raise


# ---------------------------------------------------------------------------
# run_init — happy path
# ---------------------------------------------------------------------------


def test_run_init_copies_template_files(tmp_path: Path) -> None:
    """run_init should copy template files into cwd and mark onboarding done."""
    # Build a fake templates directory
    tpl_root = tmp_path / "templates"
    tpl_dir = tpl_root / "artigo-ieee"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "exemplo.md").write_text("# Hello")
    (tpl_dir / "template.tex").write_text("\\documentclass{article}")

    dest = tmp_path / "dest"
    dest.mkdir()

    flag = tmp_path / ".onboarding_done"

    with (
        patch("mark2tex.onboarding._flag_path", return_value=flag),
        patch(
            "mark2tex.onboarding.resources.files",
            return_value=MagicMock(
                joinpath=lambda *_: MagicMock(__str__=lambda s: str(tpl_root))
            ),
        ),
        patch("mark2tex.onboarding.Path.cwd", return_value=dest),
    ):
        run_init(template="artigo-ieee")

    assert (dest / "exemplo.md").exists()
    assert (dest / "template.tex").exists()
    assert flag.exists()


def test_run_init_skips_existing_files(tmp_path: Path) -> None:
    """run_init must not overwrite files that already exist in cwd."""
    tpl_root = tmp_path / "templates"
    tpl_dir = tpl_root / "artigo-ieee"
    tpl_dir.mkdir(parents=True)
    (tpl_dir / "exemplo.md").write_text("NEW")

    dest = tmp_path / "dest"
    dest.mkdir()
    existing = dest / "exemplo.md"
    existing.write_text("ORIGINAL")

    flag = tmp_path / ".onboarding_done"

    with (
        patch("mark2tex.onboarding._flag_path", return_value=flag),
        patch(
            "mark2tex.onboarding.resources.files",
            return_value=MagicMock(
                joinpath=lambda *_: MagicMock(__str__=lambda s: str(tpl_root))
            ),
        ),
        patch("mark2tex.onboarding.Path.cwd", return_value=dest),
    ):
        run_init(template="artigo-ieee")

    assert existing.read_text() == "ORIGINAL"


def test_run_init_invalid_template(tmp_path: Path) -> None:
    """run_init with an unknown template name must not crash."""
    tpl_root = tmp_path / "templates"
    (tpl_root / "tcc-abnt").mkdir(parents=True)

    flag = tmp_path / ".onboarding_done"

    with (
        patch("mark2tex.onboarding._flag_path", return_value=flag),
        patch(
            "mark2tex.onboarding.resources.files",
            return_value=MagicMock(
                joinpath=lambda *_: MagicMock(__str__=lambda s: str(tpl_root))
            ),
        ),
    ):
        run_init(template="does-not-exist")  # must not raise

    assert not flag.exists()


# ---------------------------------------------------------------------------
# run_init — edge cases
# ---------------------------------------------------------------------------


def test_run_init_no_templates_available(tmp_path: Path) -> None:
    """run_init must handle an empty templates directory gracefully."""
    tpl_root = tmp_path / "templates"
    tpl_root.mkdir()

    flag = tmp_path / ".onboarding_done"

    with (
        patch("mark2tex.onboarding._flag_path", return_value=flag),
        patch(
            "mark2tex.onboarding.resources.files",
            return_value=MagicMock(
                joinpath=lambda *_: MagicMock(__str__=lambda s: str(tpl_root))
            ),
        ),
    ):
        run_init(template="anything")  # must not raise


def test_run_init_resources_error(tmp_path: Path) -> None:
    """run_init must handle importlib.resources failures gracefully."""
    with patch(
        "mark2tex.onboarding.resources.files", side_effect=Exception("pkg missing")
    ):
        run_init(template="artigo-ieee")  # must not raise
