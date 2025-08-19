from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Tuple, List, Callable

class EventQueue[EventType, PriorityType]:
    @dataclass
    class PriorityItem:
        priority: PriorityType
        event: EventType=field(compare=False)

        def __lt__(self, other: 'PriorityItem') -> bool:
            return self.priority < other.priority
    
    def __init__(self, maxsize=0):
        self._queue = PriorityQueue(maxsize)

    def add_event(self, event: EventType, priority: PriorityType):
        self._queue.put(self.PriorityItem(priority, event))

    def remove_event(self, predicate: Callable[[EventType], bool]):
        # Create a new queue without the event to be removed
        new_queue = PriorityQueue()
        while not self._queue.empty():
            item = self._queue.get()
            if not predicate(item.event):
                new_queue.put(item)
        self._queue = new_queue

    def get_next_event(self) -> Tuple[PriorityType, EventType]:
        item = self._queue.get()
        return item.priority, item.event
    
    def empty(self) -> bool:
        return self._queue.empty()
    
    def get_all_events(self) -> List[EventType]:
        return [item for item in list(self._queue.queue)]
        