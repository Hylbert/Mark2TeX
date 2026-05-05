from unittest.mock import MagicMock, patch

from mark2tex.setup_env import ensure_environment


def test_ensure_environment_docker_not_installed(capsys):
    with patch("shutil.which", return_value=None):
        ensure_environment()
    captured = capsys.readouterr()
    assert "docker" in captured.out.lower() or captured.out == ""


def test_ensure_environment_docker_installed_image_present():
    with patch("shutil.which", return_value="/usr/bin/docker"):
        with patch("docker.from_env") as mock_docker:
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            mock_client.images.get.return_value = MagicMock()
            ensure_environment()
