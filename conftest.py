import pytest
import tempfile
import os


@pytest.fixture
def temp_json_file():
    """Фикстура для временного JSON файла"""
    temp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    temp_file.close()

    yield temp_file.name

    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def sample_task():
    """Фикстура с экземпляром задачи"""
    from tasks import Task

    return Task("Test Task", "высокий", "2024-12-31")


@pytest.fixture
def todo_app(temp_json_file):
    """Фикстура с экземпляром приложения ToDoApp"""
    # Импортируем здесь, чтобы избежать циклических импортов
    from tasks import ToDoApp, TaskManager

    app = ToDoApp()
    # Переопределяем TaskManager с временным файлом
    app.task_manager = TaskManager(temp_json_file)
    return app
