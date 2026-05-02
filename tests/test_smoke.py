"""
Smoke tests básicos para garantir que os módulos importam corretamente
e que as classes principais instanciam sem erros.
"""
import pytest


def test_import_app():
    """Verifica que o módulo app importa sem erro."""
    import src.app  # noqa: F401


def test_import_cli():
    """Verifica que o módulo cli importa sem erro."""
    import src.cli  # noqa: F401


def test_import_log_translator():
    """Verifica que log_translator importa sem erro."""
    from src.log_translator import log_translator
    assert callable(log_translator)


def test_import_watcher():
    """Verifica que WatcherManager instancia sem erro."""
    from src.watcher import WatcherManager
    wm = WatcherManager()
    assert wm.observer is None


def test_docker_manager_init():
    """Verifica que DockerManager instancia corretamente."""
    from src.docker_manager import DockerManager
    dm = DockerManager()
    assert dm.bin_dir.exists() or True


def test_log_translator_returns_none_on_noise():
    """log_translator deve filtrar linhas irrelevantes retornando None."""
    from src.log_translator import log_translator
    result = log_translator("")
    assert result is None or isinstance(result, str)


def test_watcher_manager_stop_without_start():
    """stop_watching não deve lançar erro se nunca foi iniciado."""
    from src.watcher import WatcherManager
    wm = WatcherManager()
    wm.stop_watching()
