from unittest.mock import patch
from src.setup_env import ensure_environment

def test_ensure_environment_check_only_does_not_raise():
    # check_only=True não deve instalar nada, só verificar
    try:
        ensure_environment(check_only=True)
    except SystemExit:
        pass  # Esperado se Docker não estiver disponível no CI
    except Exception as e:
        pytest.fail(f"Raised unexpected: {e}")