import pytest
import os
from tasks import Task, TaskManager, ToDoApp


class TestTask:
    """Тесты для класса Task"""

    def test_task_initialization(self):
        """Тест инициализации задачи"""
        task = Task("Test Task", "высокий", "2024-12-31", False)

        assert task.title == "Test Task"
        assert task.priority == "высокий"
        assert task.due_date == "2024-12-31"
        assert task.completed == False
        assert hasattr(task, "created_at")
        assert isinstance(task.created_at, str)

    def test_task_initialization_default_values(self):
        """Тест инициализации с значениями по умолчанию"""
        task = Task("Test Task")

        assert task.title == "Test Task"
        assert task.priority == "средний"
        assert task.due_date == ""
        assert task.completed == False
        assert task.created_at is not None

    def test_mark_completed(self):
        """Тест отметки задачи как выполненной"""
        task = Task("Test Task")
        assert task.completed == False

        task.mark_completed()
        assert task.completed == True

    def test_edit_title(self):
        """Тест редактирования заголовка задачи"""
        task = Task("Old Title")
        task.edit(title="New Title")
        assert task.title == "New Title"

    def test_edit_priority(self):
        """Тест редактирования приоритета задачи"""
        task = Task("Test Task", "низкий")
        task.edit(priority="высокий")
        assert task.priority == "высокий"

    def test_edit_due_date(self):
        """Тест редактирования срока выполнения"""
        task = Task("Test Task")
        task.edit(due_date="2024-12-31")
        assert task.due_date == "2024-12-31"

    def test_edit_multiple_fields(self):
        """Тест одновременного редактирования нескольких полей"""
        task = Task("Old Title", "низкий", "2024-01-01")
        task.edit(title="New Title", priority="высокий", due_date="2024-12-31")

        assert task.title == "New Title"
        assert task.priority == "высокий"
        assert task.due_date == "2024-12-31"

    def test_edit_partial(self):
        """Тест частичного редактирования"""
        task = Task("Original Title", "средний", "2024-01-01")
        task.edit(title="New Title")

        assert task.title == "New Title"
        assert task.priority == "средний"
        assert task.due_date == "2024-01-01"

    def test_show_completed(self):
        """Тест отображения выполненной задачи"""
        task = Task("Test Task", "высокий", "2024-12-31", True)
        result = task.show()

        assert "[ВЫПОЛНЕНО]" in result
        assert "Test Task" in result
        assert "ВЫСОКИЙ" in result
        assert "2024-12-31" in result

    def test_show_not_completed(self):
        """Тест отображения невыполненной задачи"""
        task = Task("Test Task", "низкий", "", False)
        result = task.show()

        assert "[НЕ ВЫПОЛНЕНО]" in result
        assert "Test Task" in result
        assert "НИЗКИЙ" in result
        assert "Создана:" in result

    def test_to_dict(self):
        """Тест преобразования задачи в словарь"""
        task = Task("Test Task", "средний", "2024-12-31", True)
        task_dict = task.to_dict()

        assert task_dict["title"] == "Test Task"
        assert task_dict["priority"] == "средний"
        assert task_dict["due_date"] == "2024-12-31"
        assert task_dict["completed"] == True
        assert "created_at" in task_dict

    def test_from_dict(self):
        """Тест создания задачи из словаря"""
        data = {
            "title": "Test Task",
            "priority": "высокий",
            "due_date": "2024-12-31",
            "completed": False,
            "created_at": "2024-01-01 10:00:00",
        }

        task = Task.from_dict(data)

        assert task.title == "Test Task"
        assert task.priority == "высокий"
        assert task.due_date == "2024-12-31"
        assert task.completed == False
        assert task.created_at == "2024-01-01 10:00:00"

    def test_priority_lowercase_conversion(self):
        """Тест приведения приоритета к нижнему регистру"""
        task1 = Task("Task 1", "ВЫСОКИЙ")
        task2 = Task("Task 2", "Средний")
        task3 = Task("Task 3", "НИЗКИЙ")

        assert task1.priority == "высокий"
        assert task2.priority == "средний"
        assert task3.priority == "низкий"


class TestTaskManager:
    """Тесты для класса TaskManager"""

    def test_task_manager_initialization(self, temp_json_file):
        """Тест инициализации менеджера задач"""
        manager = TaskManager(temp_json_file)
        assert manager.tasks == []
        assert manager.filename == temp_json_file

    def test_add_task_valid(self, temp_json_file):
        """Тест добавления валидной задачи"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Test Task", "высокий", "2024-12-31")

        assert len(manager.tasks) == 1
        assert manager.tasks[0].title == "Test Task"
        assert manager.tasks[0].priority == "высокий"
        assert manager.tasks[0].due_date == "2024-12-31"

    def test_add_task_empty_title(self, temp_json_file, capsys):
        """Тест добавления задачи с пустым заголовком"""
        manager = TaskManager(temp_json_file)
        manager.add_task("", "высокий")

        captured = capsys.readouterr()
        assert "Ошибка: описание задачи не может быть пустым!" in captured.out
        assert len(manager.tasks) == 0

    def test_add_task_invalid_priority(self, temp_json_file, capsys):
        """Тест добавления задачи с невалидным приоритетом"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Test Task", "неправильный")

        captured = capsys.readouterr()
        assert "Ошибка: приоритет должен быть один из:" in captured.out
        assert len(manager.tasks) == 0

    def test_add_task_case_insensitive_priority(self, temp_json_file):
        """Тест добавления задачи с приоритетом в разных регистрах"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "ВЫСОКИЙ")
        manager.add_task("Task 2", "Средний")
        manager.add_task("Task 3", "низкий")

        assert len(manager.tasks) == 3
        assert manager.tasks[0].priority == "высокий"
        assert manager.tasks[1].priority == "средний"
        assert manager.tasks[2].priority == "низкий"

    def test_remove_task_valid(self, temp_json_file):
        """Тест удаления существующей задачи"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")
        manager.add_task("Task 2", "средний")

        assert len(manager.tasks) == 2
        result = manager.remove_task(0)

        assert result == True
        assert len(manager.tasks) == 1
        assert manager.tasks[0].title == "Task 2"

    def test_remove_task_invalid_index(self, temp_json_file, capsys):
        """Тест удаления несуществующей задачи"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        result = manager.remove_task(5)

        captured = capsys.readouterr()
        assert result == False
        assert "не найдена" in captured.out
        assert len(manager.tasks) == 1

    def test_remove_task_negative_index(self, temp_json_file, capsys):
        """Тест удаления задачи с отрицательным индексом"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        result = manager.remove_task(-1)

        captured = capsys.readouterr()
        assert result == False
        assert len(manager.tasks) == 1

    def test_edit_task_valid(self, temp_json_file):
        """Тест редактирования существующей задачи"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Old Title", "низкий", "2024-01-01")

        result = manager.edit_task(
            0, title="New Title", priority="высокий", due_date="2024-12-31"
        )

        assert result == True
        assert manager.tasks[0].title == "New Title"
        assert manager.tasks[0].priority == "высокий"
        assert manager.tasks[0].due_date == "2024-12-31"

    def test_edit_task_invalid_index(self, temp_json_file, capsys):
        """Тест редактирования несуществующей задачи"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        result = manager.edit_task(5, title="New Title")

        captured = capsys.readouterr()
        assert result == False
        assert "не найдена" in captured.out
        assert manager.tasks[0].title == "Task 1"

    def test_mark_task_completed(self, temp_json_file):
        """Тест отметки задачи как выполненной"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        assert manager.tasks[0].completed == False
        result = manager.mark_task_completed(0)

        assert result == True
        assert manager.tasks[0].completed == True

    def test_mark_task_completed_invalid_index(self, temp_json_file, capsys):
        """Тест отметки несуществующей задачи как выполненной"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        result = manager.mark_task_completed(5)

        captured = capsys.readouterr()
        assert result == False
        assert manager.tasks[0].completed == False

    @pytest.mark.parametrize(
        "status_filter,expected_count",
        [
            ("все", 3),
            ("выполненные", 1),
            ("невыполненные", 2),
        ],
    )
    def test_list_tasks_filter(
        self, temp_json_file, capsys, status_filter, expected_count
    ):
        """Тест фильтрации задач по статусу"""
        manager = TaskManager(temp_json_file)

        # Добавляем 3 задачи, одна из которых выполненная
        manager.add_task("Task 1", "высокий")
        manager.add_task("Task 2", "средний")
        manager.add_task("Task 3", "низкий")
        manager.mark_task_completed(1)  # Отмечаем вторую как выполненную

        manager.list_tasks(status_filter)

        captured = capsys.readouterr()
        assert "СПИСОК ЗАДАЧ" in captured.out
        assert f"фильтр: {status_filter}" in captured.out

        # Подсчитываем количество задач в выводе
        task_count = captured.out.count("Задача #")
        assert task_count == expected_count

    def test_list_tasks_empty(self, temp_json_file, capsys):
        """Тест вывода пустого списка задач"""
        manager = TaskManager(temp_json_file)
        manager.list_tasks("все")

        captured = capsys.readouterr()
        assert "Список задач пуст!" in captured.out

    def test_list_tasks_filter_no_results(self, temp_json_file, capsys):
        """Тест фильтрации без результатов"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Task 1", "высокий")

        manager.list_tasks("выполненные")

        captured = capsys.readouterr()
        assert "Нет задач с фильтром" in captured.out

    def test_save_and_load_from_file(self, temp_json_file):
        """Тест сохранения и загрузки из файла"""
        # Создаем первый менеджер и добавляем задачи
        manager1 = TaskManager(temp_json_file)
        manager1.add_task("Task 1", "высокий", "2024-12-31")
        manager1.add_task("Task 2", "средний")
        manager1.mark_task_completed(0)

        # Создаем второй менеджер и загружаем задачи
        manager2 = TaskManager(temp_json_file)

        assert len(manager2.tasks) == 2
        assert manager2.tasks[0].title == "Task 1"
        assert manager2.tasks[0].completed == True
        assert manager2.tasks[0].priority == "высокий"
        assert manager2.tasks[0].due_date == "2024-12-31"
        assert manager2.tasks[1].title == "Task 2"
        assert manager2.tasks[1].completed == False

    def test_load_from_nonexistent_file(self, temp_json_file):
        """Тест загрузки из несуществующего файла"""
        # Удаляем файл, если он существует
        if os.path.exists(temp_json_file):
            os.remove(temp_json_file)

        manager = TaskManager(temp_json_file)
        assert manager.tasks == []

    def test_save_to_file_error(self, temp_json_file, mocker):
        """Тест обработки ошибки при сохранении"""
        manager = TaskManager(temp_json_file)
        manager.add_task("Test Task", "высокий")

        # Мокаем открытие файла для имитации ошибки
        mocker.patch("builtins.open", side_effect=Exception("Test error"))

        # Не должно вызывать исключение
        manager.save_to_file()

    def test_load_from_file_error(self, temp_json_file, mocker, capsys):
        """Тест обработки ошибки при загрузке"""
        # Создаем невалидный JSON файл
        with open(temp_json_file, "w") as f:
            f.write("invalid json")

        manager = TaskManager(temp_json_file)

        captured = capsys.readouterr()
        assert "Ошибка при загрузке файла" in captured.out
        assert manager.tasks == []

    @pytest.mark.slow
    def test_performance_add_multiple_tasks(self, temp_json_file):
        """Тест производительности при добавлении множества задач"""
        manager = TaskManager(temp_json_file)

        for i in range(100):
            manager.add_task(f"Task {i}", "средний")

        assert len(manager.tasks) == 100

    @pytest.mark.integration
    def test_integration_workflow(self, temp_json_file):
        """Интеграционный тест полного рабочего процесса"""
        manager = TaskManager(temp_json_file)

        # 1. Добавление задач
        manager.add_task("Task 1", "высокий", "2024-12-31")
        manager.add_task("Task 2", "средний")
        manager.add_task("Task 3", "низкий", "2024-06-30")

        assert len(manager.tasks) == 3

        # 2. Редактирование задачи
        manager.edit_task(1, title="Updated Task 2", priority="высокий")
        assert manager.tasks[1].title == "Updated Task 2"
        assert manager.tasks[1].priority == "высокий"

        # 3. Отметка как выполненной
        manager.mark_task_completed(0)
        assert manager.tasks[0].completed == True

        # 4. Удаление задачи
        manager.remove_task(2)
        assert len(manager.tasks) == 2

        # 5. Сохранение и загрузка
        manager.save_to_file()

        new_manager = TaskManager(temp_json_file)
        assert len(new_manager.tasks) == 2


class TestToDoApp:
    """Тесты для класса ToDoApp"""

    def test_todoapp_initialization(self):
        """Тест инициализации приложения"""
        app = ToDoApp()
        assert hasattr(app, "task_manager")
        assert isinstance(app.task_manager, TaskManager)

    def test_show_menu(self, capsys):
        """Тест отображения меню"""
        app = ToDoApp()
        app.show_menu()

        captured = capsys.readouterr()
        assert "TO-DO LIST МЕНЕДЖЕР" in captured.out
        assert "1. Показать все задачи" in captured.out
        assert "0. Выйти" in captured.out

    @pytest.mark.ui
    def test_get_user_choice(self, monkeypatch):
        """Тест получения выбора пользователя"""
        app = ToDoApp()

        # Имитируем ввод пользователя
        monkeypatch.setattr("builtins.input", lambda _: "3")
        choice = app.get_user_choice()
        assert choice == "3"

    @pytest.mark.ui
    def test_add_task_interactive_valid(self, monkeypatch, capsys, temp_json_file):
        """Тест интерактивного добавления валидной задачи"""
        app = ToDoApp()
        # Используем временный файл
        app.task_manager = TaskManager(temp_json_file)

        # Имитируем ввод пользователя
        inputs = ["Test Task", "3", "2024-12-31"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        app.add_task_interactive()

        captured = capsys.readouterr()
        assert "ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ" in captured.out
        assert len(app.task_manager.tasks) == 1
        assert app.task_manager.tasks[0].title == "Test Task"
        assert app.task_manager.tasks[0].priority == "высокий"
        assert app.task_manager.tasks[0].due_date == "2024-12-31"

    @pytest.mark.ui
    def test_add_task_interactive_empty_title(
        self, monkeypatch, capsys, temp_json_file
    ):
        """Тест интерактивного добавления задачи с пустым заголовком"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        # Имитируем пустой ввод
        inputs = ["", "", ""]  # Пустой заголовок
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        app.add_task_interactive()

        captured = capsys.readouterr()
        assert "Ошибка: описание не может быть пустым!" in captured.out
        assert len(app.task_manager.tasks) == 0

    @pytest.mark.ui
    def test_add_task_interactive_default_priority(
        self, monkeypatch, capsys, temp_json_file
    ):
        """Тест интерактивного добавления задачи с приоритетом по умолчанию"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        inputs = ["Test Task", "", ""]  # Пустой ввод для приоритета
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        app.add_task_interactive()

        captured = capsys.readouterr()
        assert "ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ" in captured.out
        assert len(app.task_manager.tasks) == 1
        assert app.task_manager.tasks[0].priority == "средний"

    @pytest.mark.ui
    def test_edit_task_interactive_valid(self, monkeypatch, capsys, temp_json_file):
        """Тест интерактивного редактирования валидной задачи"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        # Сначала добавляем задачу
        app.task_manager.add_task("Old Title", "низкий", "2024-01-01")

        # Имитируем ввод для редактирования
        inputs = ["0", "New Title", "3", "2024-12-31"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        app.edit_task_interactive()

        captured = capsys.readouterr()
        assert "РЕДАКТИРОВАНИЕ ЗАДАЧИ" in captured.out
        assert len(app.task_manager.tasks) == 1
        assert app.task_manager.tasks[0].title == "New Title"
        assert app.task_manager.tasks[0].priority == "высокий"
        assert app.task_manager.tasks[0].due_date == "2024-12-31"

    @pytest.mark.ui
    def test_edit_task_interactive_empty_list(self, capsys, temp_json_file):
        """Тест интерактивного редактирования при пустом списке"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        app.edit_task_interactive()

        captured = capsys.readouterr()
        assert "Нет задач для редактирования!" in captured.out

    @pytest.mark.ui
    def test_mark_task_completed_interactive(self, monkeypatch, temp_json_file):
        """Тест интерактивной отметки задачи как выполненной"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        # Сначала добавляем задачу
        app.task_manager.add_task("Test Task", "высокий")

        # Имитируем ввод
        monkeypatch.setattr("builtins.input", lambda _: "0")

        app.mark_task_completed_interactive()

        assert len(app.task_manager.tasks) == 1
        assert app.task_manager.tasks[0].completed == True

    @pytest.mark.ui
    def test_remove_task_interactive(self, monkeypatch, temp_json_file):
        """Тест интерактивного удаления задачи"""
        app = ToDoApp()
        app.task_manager = TaskManager(temp_json_file)

        # Сначала добавляем задачи
        app.task_manager.add_task("Task 1", "высокий")
        app.task_manager.add_task("Task 2", "средний")

        # Имитируем ввод для удаления первой задачи
        monkeypatch.setattr("builtins.input", lambda _: "0")

        app.remove_task_interactive()

        assert len(app.task_manager.tasks) == 1
        assert app.task_manager.tasks[0].title == "Task 2"

    @pytest.mark.ui
    def test_start_exit_immediately(self, monkeypatch, capsys):
        """Тест запуска приложения с немедленным выходом"""
        app = ToDoApp()

        inputs = ["0"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))
        try:

            app.start()
        except StopIteration:
            pass

        # Проверяем что метод существует
        assert hasattr(app, "start")
        assert callable(app.start)
