import pytest

from app.in_memory_store import clear_registry
from app.task_11_2_app import reset_task_11_2_store


@pytest.fixture(autouse=True)
def _reset_in_memory_registry() -> None:
    """Изоляция in-memory реестра между тестами (задание 11.1)."""
    clear_registry()
    yield
    clear_registry()


@pytest.fixture(autouse=True)
def _reset_task_11_2_db() -> None:
    """Изоляция хранилища задания 11.2 между тестами."""
    reset_task_11_2_store()
    yield
    reset_task_11_2_store()
