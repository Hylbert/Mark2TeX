import pytest


def test_import_app():
    import mark2tex.app  # noqa: F401


def test_import_cli():
    import mark2tex.cli  # noqa: F401


def test_import_log_translator():
    from mark2tex.log_translator import log_translator
    assert callable(log_translator)


def test_import_watcher():
    from mark2tex.watcher import WatcherManager
    assert WatcherManager is not None


def test_import_docker_manager():
    from mark2tex.docker_manager import DockerManager
    assert DockerManager is not None


def test_log_translator_callable():
    from mark2tex.log_translator import log_translator
    assert callable(log_translator)


def test_watcher_manager_exists():
    from mark2tex.watcher import WatcherManager
    assert WatcherManager is not None
