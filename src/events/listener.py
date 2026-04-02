from abc import ABC, abstractmethod
from typing import TypeVar, Any, Generic, Type, Callable
from collections import defaultdict

from src.events.event_queue import EventQueue
from src.state.pokestate_defs import PokemonId

DataType = TypeVar("DataType")


class Listener(Generic[DataType], ABC):
    datatype: Type[DataType]

    @abstractmethod
    def on_event(self, input: DataType, event_queue: EventQueue) -> bool:
        pass


class ListenerManager:
    def __init__(self):
        self.listeners = defaultdict(list[Listener])
        self.ids = defaultdict(list[PokemonId])

    def add_listener(self, id: PokemonId, listener: Listener[DataType]):
        print(f"Adding listener: {listener} to {listener.datatype}")
        self.listeners[listener.datatype].append(listener)
        self.ids[listener.datatype].append(id)

    def remove_listener(self, input_id: PokemonId, pred: Callable[[Listener], bool]):
        for id, listener in zip(self.ids, self.listeners):
            if id == input_id and pred(listener):
                self.listeners[listener.datatype].remove(listener)
                self.ids[listener.datatype].remove(id)

    def remove_listener_if(self, datatype: type, pred: Callable[[Listener], bool]):
        """Remove all listeners of the given datatype that match pred."""
        keep = [
            (listener, pid)
            for listener, pid in zip(self.listeners[datatype], self.ids[datatype])
            if not pred(listener)
        ]
        self.listeners[datatype] = [listener for listener, _ in keep]
        self.ids[datatype] = [pid for _, pid in keep]

    def listen(self, datatype: Any, event_queue: EventQueue):
        listeners_to_remove = []
        for listener in self.listeners[type(datatype)]:
            if not listener.on_event(datatype, event_queue=event_queue):
                listeners_to_remove.append(listener)
        for listener in listeners_to_remove:
            self.listeners[type(datatype)].remove(listener)
