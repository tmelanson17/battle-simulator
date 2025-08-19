from abc import ABC, abstractmethod
from typing import TypeVar, Any, Generic, Type
from collections import defaultdict

from src.events.event_queue import EventQueue

DataType = TypeVar("DataType")
class Listener(Generic[DataType], ABC):
    datatype: Type[DataType]

    @abstractmethod
    def on_event(self, input: DataType, event_queue: EventQueue):
        pass


class ListenerManager:
    def __init__(self):
        self.listeners = defaultdict(list[Listener])

    def add_listener(self, listener: Listener[DataType]):
        print(f"Adding listener: {listener} to {listener.datatype}")
        self.listeners[listener.datatype].append(listener)

    def remove_listener(self, listener: Listener[DataType]):
        self.listeners[listener.datatype].remove(listener)

    def listen(self, datatype: Any, event_queue: EventQueue):
        for listener in self.listeners[type(datatype)]:
            listener.on_event(datatype, event_queue=event_queue)