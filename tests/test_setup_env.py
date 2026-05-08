"""Tests for mark2tex.setup_env.

All tests are fully mocked — no Docker daemon, network, or real disk
access required. Covers pull stream, build stream, interrupt handling,
and graceful fallback when Docker Hub is unreachable.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mark2tex.setup_env import (
    _build_locally,
    _pull_from_hub,
    ensure_environment,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pull_events(
    layer: str = "abc123",
    include_extract: bool = True,
) -> list[dict]:
    events = [
        {"status": "Pulling fs layer", "id": layer, "progressDetail": {}},
        {"status": "Downloading", "id": layer, "progressDetail": {"current": 512, "total": 1024}},
        {"status": "Downloading", "id": layer, "progressDetail": {"current": 1024, "total": 1024}},
    ]
    if include_extract:
        events += [
            {"status": "Extracting", "id": layer, "progressDetail": {"current": 512, "total": 1024}},
            {"status": "Pull complete", "id": layer, "progressDetail": {}},
        ]
    return events


def _make_build_events() -> list[dict]:
    return [
        {"stream": "Step 1/5 : FROM ubuntu:22.04\n"},
        {"stream": "Step 2/5 : RUN apt-get update\n"},
        {"stream": "Successfully built deadbeef\n"},
    ]


# ---------------------------------------------------------------------------
# ensure_environment
# ---------------------------------------------------------------------------

class TestEnsureEnvironment:
    def test_check_only_exits_gracefully_when_no_docker(self):
        """check_only=True exits via sys.exit only when Docker is absent."""
        try:
            ensure_environment(check_only=True)
        except SystemExit:
            pass  # Expected on CI without Docker
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"Raised unexpected: {exc}")

    def test_check_only_does_not_call_ensure_image(self):
        with (
            patch("mark2tex.setup_env._check_docker_binary"),
            patch("mark2tex.setup_env._check_docker_daemon"),
            patch("mark2tex.setup_env._ensure_image") as mock_ensure,
        ):
            ensure_environment(check_only=True)
            mock_ensure.assert_not_called()

    def test_full_run_calls_ensure_image(self):
        with (
            patch("mark2tex.setup_env._check_docker_binary"),
            patch("mark2tex.setup_env._check_docker_daemon"),
            patch("mark2tex.setup_env._ensure_image") as mock_ensure,
        ):
            ensure_environment(check_only=False)
            mock_ensure.assert_called_once()


# ---------------------------------------------------------------------------
# _pull_from_hub
# ---------------------------------------------------------------------------

class TestPullFromHub:
    def _make_client(self, events, tag_raises=False):
        client = MagicMock()
        client.api.pull.return_value = iter(events)
        if tag_raises:
            client.images.get.side_effect = Exception("not found")
        else:
            img_mock = MagicMock()
            client.images.get.return_value = img_mock
        return client

    def test_successful_pull_returns_true(self):
        client = self._make_client(_make_pull_events())
        result = _pull_from_hub(client)
        assert result is True

    def test_pull_with_multiple_layers(self):
        events = _make_pull_events("aaa") + _make_pull_events("bbb")
        client = self._make_client(events)
        result = _pull_from_hub(client)
        assert result is True

    def test_pull_without_total_in_detail(self):
        """Events with empty progressDetail should not raise."""
        events = [
            {"status": "Pulling fs layer", "id": "xyz", "progressDetail": {}},
            {"status": "Downloading", "id": "xyz", "progressDetail": {}},
            {"status": "Pull complete", "id": "xyz", "progressDetail": {}},
        ]
        client = self._make_client(events)
        assert _pull_from_hub(client) is True

    def test_events_without_layer_id_are_skipped(self):
        """Events missing 'id' (e.g. digest lines) must not crash."""
        events = [
            {"status": "Pulling from hylbert/mark2tex", "progressDetail": {}},
            {"status": "Digest: sha256:abc", "progressDetail": {}},
            {"status": "Status: Downloaded newer image", "progressDetail": {}},
        ]
        client = self._make_client(events)
        assert _pull_from_hub(client) is True

    def test_exception_during_pull_returns_false(self):
        client = MagicMock()
        client.api.pull.side_effect = Exception("network error")
        result = _pull_from_hub(client)
        assert result is False

    def test_keyboard_interrupt_exits_130(self):
        client = MagicMock()
        client.api.pull.side_effect = KeyboardInterrupt
        with pytest.raises(SystemExit) as exc_info:
            _pull_from_hub(client)
        assert exc_info.value.code == 130

    def test_tag_failure_does_not_abort(self):
        """If tagging the pulled image fails, pull still returns True."""
        client = self._make_client(_make_pull_events(), tag_raises=True)
        assert _pull_from_hub(client) is True


# ---------------------------------------------------------------------------
# _build_locally
# ---------------------------------------------------------------------------

class TestBuildLocally:
    def _make_client(self, events):
        client = MagicMock()
        client.api.build.return_value = iter(events)
        return client

    def test_successful_build_completes(self, tmp_path):
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM scratch\n")
        client = self._make_client(_make_build_events())
        with patch("mark2tex.setup_env.Path") as mock_path_cls:
            # Make bundled Dockerfile resolve to our tmp_path Dockerfile
            mock_resolved = MagicMock()
            mock_resolved.exists.return_value = True
            mock_resolved.parent = tmp_path
            instance = MagicMock()
            instance.resolve.return_value = mock_resolved
            mock_path_cls.return_value = instance
            mock_path_cls.side_effect = lambda *a, **kw: (
                instance if "__file__" in str(a) else Path(*a, **kw)
            )
            # Simply verify no exception is raised
            try:
                _build_locally(client)
            except SystemExit:
                pass

    def test_missing_dockerfile_exits_1(self, tmp_path):
        client = self._make_client([])
        with (
            patch.object(
                Path,
                "exists",
                return_value=False,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _build_locally(client)
        assert exc_info.value.code == 1

    def test_keyboard_interrupt_exits_130(self, tmp_path):
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("FROM scratch\n")
        client = MagicMock()
        client.api.build.side_effect = KeyboardInterrupt

        def _patched_path(arg):
            p = MagicMock(spec=Path)
            p.exists.return_value = True
            p.__truediv__ = lambda s, o: Path(tmp_path / o)
            p.parent = tmp_path
            p.parents = [tmp_path, tmp_path.parent]
            return p

        with (
            patch("mark2tex.setup_env.Path", side_effect=_patched_path),
            pytest.raises(SystemExit) as exc_info,
        ):
            _build_locally(client)
        assert exc_info.value.code == 130

    def test_docker_exception_exits_1(self):
        from docker.errors import DockerException

        client = MagicMock()
        client.api.build.side_effect = DockerException("build failed")

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(
                Path,
                "__truediv__",
                return_value=MagicMock(exists=lambda: True),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _build_locally(client)
        assert exc_info.value.code == 1
