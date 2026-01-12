import json
import os
from datetime import datetime
from typing import List, Optional


class Task:
    """Класс, представляющий отдельную задачу"""

    def __init__(
        self,
        title: str,
        priority: str = "средний",
        due_date: str = "",
        completed: bool = False,
    ):
        self.title = title
        self.priority = priority.lower()
        self.due_date = due_date
        self.completed = completed
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def mark_completed(self) -> None:
        """Отметить задачу как выполненную"""
        self.completed = True

    def edit(
        self,
        title: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> None:
        """Редактировать параметры задачи"""
        if title:
            self.title = title
        if priority:
            self.priority = priority.lower()
        if due_date:
            self.due_date = due_date

    def show(self) -> str:
        """Вывести информацию о задаче в виде строки"""
        status = "ВЫПОЛНЕНО" if self.completed else "НЕ ВЫПОЛНЕНО"
        priority_display = f"{self.priority.upper()}"

        result = f"[{status}] {self.title}\n"
        result += f"   Приоритет: {priority_display}\n"
        result += f"   Создана: {self.created_at}\n"
        if self.due_date:
            result += f"   Срок: {self.due_date}\n"
        return result

    def to_dict(self) -> dict:
        """Преобразовать задачу в словарь для сохранения в файл"""
        return {
            "title": self.title,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Создать задачу из словаря (при загрузке из файла)"""
        task = cls(data["title"], data["priority"], data["due_date"], data["completed"])
        task.created_at = data["created_at"]
        return task


class TaskManager:
    """Класс для управления списком задач"""

    def __init__(self, filename: str = "tasks.json"):
        self.tasks: List[Task] = []
        self.filename = filename
        self.load_from_file()

    def add_task(
        self, title: str, priority: str = "средний", due_date: str = ""
    ) -> None:
        """Добавить новую задачу"""
        if not title.strip():
            print("Ошибка: описание задачи не может быть пустым!")
            return

        valid_priorities = ["низкий", "средний", "высокий"]
        if priority.lower() not in valid_priorities:
            print(
                f"Ошибка: приоритет должен быть один из: {', '.join(valid_priorities)}"
            )
            return

        task = Task(title, priority, due_date)
        self.tasks.append(task)
        print(f"Задача '{title}' успешно добавлена!")
        self.save_to_file()

    def remove_task(self, task_index: int) -> bool:
        """Удалить задачу по индексу"""
        if 0 <= task_index < len(self.tasks):
            removed_task = self.tasks.pop(task_index)
            print(f"Задача '{removed_task.title}' успешно удалена!")
            self.save_to_file()
            return True
        else:
            print(f"Ошибка: задача с индексом {task_index} не найдена!")
            return False

    def edit_task(self, task_index: int, **kwargs) -> bool:
        """Редактировать выбранную задачу"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].edit(**kwargs)
            print(f"Задача '{self.tasks[task_index].title}' успешно отредактирована!")
            self.save_to_file()
            return True
        else:
            print(f"Ошибка: задача с индексом {task_index} не найдена!")
            return False

    def mark_task_completed(self, task_index: int) -> bool:
        """Отметить задачу как выполненную"""
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index].mark_completed()
            print(f"Задача '{self.tasks[task_index].title}' отмечена как выполненная!")
            self.save_to_file()
            return True
        else:
            print(f"Ошибка: задача с индексом {task_index} не найдена!")
            return False

    def list_tasks(self, status_filter: str = "все") -> None:
        """Вывести список задач с фильтрацией"""
        if not self.tasks:
            print("Список задач пуст!")
            return

        filtered_tasks = []

        if status_filter == "выполненные":
            filtered_tasks = [task for task in self.tasks if task.completed]
        elif status_filter == "невыполненные":
            filtered_tasks = [task for task in self.tasks if not task.completed]
        else:  # 'все'
            filtered_tasks = self.tasks

        if not filtered_tasks:
            print(f"Нет задач с фильтром '{status_filter}'!")
            return

        print(f"\n" + "=" * 50)
        print(f"СПИСОК ЗАДАЧ (фильтр: {status_filter}):")
        print("=" * 50)

        for i, task in enumerate(filtered_tasks):
            print(f"\nЗадача #{i}:")
            print(task.show())

        print(f"\nВсего задач: {len(filtered_tasks)}")

    def save_to_file(self) -> None:
        """Сохранить список задач в файл JSON"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks]
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении файла: {e}")

    def load_from_file(self) -> None:
        """Загрузить список задач из файла JSON"""
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            self.tasks = [Task.from_dict(data) for data in tasks_data]
            print(f"Загружено {len(self.tasks)} задач из файла")
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            self.tasks = []


class ToDoApp:
    """Класс приложения To-Do List"""

    def __init__(self):
        """Инициализация приложения"""
        self.task_manager = TaskManager()

    def show_menu(self) -> None:
        """Показать главное меню"""
        print("\n" + "=" * 50)
        print("TO-DO LIST МЕНЕДЖЕР")
        print("=" * 50)
        print("1. Показать все задачи")
        print("2. Показать невыполненные задачи")
        print("3. Показать выполненные задачи")
        print("4. Добавить новую задачу")
        print("5. Редактировать задачу")
        print("6. Отметить задачу как выполненную")
        print("7. Удалить задачу")
        print("8. Сохранить задачи в файл")
        print("9. Загрузить задачи из файла")
        print("0. Выйти")
        print("=" * 50)

    def get_user_choice(self) -> str:
        """Получить выбор пользователя"""
        return input("\nВыберите действие (0-9): ").strip()

    def add_task_interactive(self) -> None:
        """Интерактивное добавление задачи"""
        print("\n" + "-" * 40)
        print("ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ")
        print("-" * 40)

        title = input("Введите описание задачи: ").strip()
        if not title:
            print("Ошибка: описание не может быть пустым!")
            return

        print("\nВыберите приоритет:")
        print("1. Низкий")
        print("2. Средний")
        print("3. Высокий")

        priority_choice = input("Ваш выбор (1-3, по умолчанию 2): ").strip()
        priority_map = {"1": "низкий", "2": "средний", "3": "высокий"}
        priority = priority_map.get(priority_choice, "средний")

        due_date = input(
            "Введите срок выполнения (ГГГГ-ММ-ДД или оставьте пустым): "
        ).strip()

        self.task_manager.add_task(title, priority, due_date)

    def edit_task_interactive(self) -> None:
        """Интерактивное редактирование задачи"""
        if not self.task_manager.tasks:
            print("Нет задач для редактирования!")
            return

        self.task_manager.list_tasks("все")

        try:
            task_index = int(
                input("\nВведите номер задачи для редактирования: ").strip()
            )
        except ValueError:
            print("Ошибка: введите число!")
            return

        if not (0 <= task_index < len(self.task_manager.tasks)):
            print(f"Ошибка: задача с номером {task_index} не найдена!")
            return

        print("\n" + "-" * 40)
        print("РЕДАКТИРОВАНИЕ ЗАДАЧИ")
        print("-" * 40)

        title = input(
            f"Новое описание [{self.task_manager.tasks[task_index].title}]: "
        ).strip()
        title = title if title else None

        print("\nВыберите новый приоритет:")
        print("1. Низкий")
        print("2. Средний")
        print("3. Высокий")

        priority_choice = input("Ваш выбор (1-3 или Enter для пропуска): ").strip()
        priority_map = {"1": "низкий", "2": "средний", "3": "высокий"}
        priority = priority_map.get(priority_choice) if priority_choice else None

        current_due = self.task_manager.tasks[task_index].due_date
        due_date = input(f"Новый срок выполнения [{current_due}]: ").strip()
        due_date = due_date if due_date else None

        self.task_manager.edit_task(
            task_index, title=title, priority=priority, due_date=due_date
        )

    def mark_task_completed_interactive(self) -> None:
        """Интерактивная отметка задачи как выполненной"""
        if not self.task_manager.tasks:
            print("Нет задач!")
            return

        self.task_manager.list_tasks("невыполненные")

        try:
            task_index = int(
                input("\nВведите номер задачи для отметки как выполненной: ").strip()
            )
        except ValueError:
            print("Ошибка: введите число!")
            return

        self.task_manager.mark_task_completed(task_index)

    def remove_task_interactive(self) -> None:
        """Интерактивное удаление задачи"""
        if not self.task_manager.tasks:
            print("Нет задач для удаления!")
            return

        self.task_manager.list_tasks("все")

        try:
            task_index = int(input("\nВведите номер задачи для удаления: ").strip())
        except ValueError:
            print("Ошибка: введите число!")
            return

        self.task_manager.remove_task(task_index)

    def start(self) -> None:
        """Запуск основного цикла программы"""
        print("Добро пожаловать в To-Do List Manager!")
        print("Версия 1.0")

        while True:
            self.show_menu()
            choice = self.get_user_choice()

            if choice == "0":
                print("\nДо свидания! Спасибо за использование To-Do List Manager!")
                break

            elif choice == "1":
                self.task_manager.list_tasks("все")

            elif choice == "2":
                self.task_manager.list_tasks("невыполненные")

            elif choice == "3":
                self.task_manager.list_tasks("выполненные")

            elif choice == "4":
                self.add_task_interactive()

            elif choice == "5":
                self.edit_task_interactive()

            elif choice == "6":
                self.mark_task_completed_interactive()

            elif choice == "7":
                self.remove_task_interactive()

            elif choice == "8":
                self.task_manager.save_to_file()
                print("Задачи успешно сохранены в файл!")

            elif choice == "9":
                self.task_manager.load_from_file()

            else:
                print("Неверный выбор! Попробуйте снова.")

            input("\nНажмите Enter для продолжения...")


def main():
    app = ToDoApp()
    app.start()


if __name__ == "__main__":
    main()
