import abc
import asyncio
from typing import Coroutine, Any

"""
Описание задачи:
    Необходимо реализовать планировщик, позволяющий запускать и отслеживать фоновые корутины.
    Планировщик должен обеспечивать:
        - возможность планирования новой задачи
        - отслеживание состояния завершенных задач (сохранение результатов их выполнения)
        - отмену незавершенных задач перед остановкой работы планировщика
        
    Ниже представлен интерфейс, которому должна соответствовать ваша реализация.
    
    Обратите внимание, что перед завершением работы планировщика, все запущенные им корутины должны быть
    корректным образом завершены.
    
    В папке tests вы найдете тесты, с помощью которых мы будем проверять работоспособность вашей реализации
    
"""


class AbstractRegistrator(abc.ABC):
    """
    Сохраняет результаты работы завершенных задач.
    В тестах мы передадим в ваш Watcher нашу реализацию Registrator и проверим корректность сохранения результатов.
    """

    @abc.abstractmethod
    def register_value(self, value: Any) -> None:
        # Store values returned from done task
        ...

    @abc.abstractmethod
    def register_error(self, error: BaseException) -> None:
        # Store exceptions returned from done task
        ...


class AbstractWatcher(abc.ABC):
    """
    Абстрактный интерфейс, которому должна соответсововать ваша реализация Watcher.
    При тестировании мы расчитываем на то, что этот интерфейс будет соблюден.
    """

    def __init__(self, registrator: AbstractRegistrator):
        self.registrator = registrator  # we expect to find registrator here

    @abc.abstractmethod
    async def start(self) -> None:
        # Good idea is to implement here all necessary for start watcher :)
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        # Method will be called on the end of the Watcher's work
        ...

    @abc.abstractmethod
    def start_and_watch(self, coro: Coroutine) -> None:
        # Start new task and put to watching
        ...


class StudentWatcher(AbstractWatcher):
    def __init__(self, registrator: AbstractRegistrator):
        super().__init__(registrator)
        self.tasks = []
        self.is_started = False
        self.registrator = registrator

    async def start(self) -> None:
        self.is_started = True

    async def stop(self) -> None:
        done_tasks, pending_tasks = await asyncio.wait(self.tasks)

        for task in done_tasks:
            try:
                self.registrator.register_value(task.result())
            except Exception as e:
                self.registrator.register_error(e)

        for task in pending_tasks:
            task.cancel()

        self.is_started = False
        self.tasks = []

    def start_and_watch(self, coro: Coroutine) -> None:
        self.is_started = True
        self.tasks.append(asyncio.create_task(coro))
