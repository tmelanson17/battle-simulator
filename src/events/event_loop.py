from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Tuple

class EventLoop[EventType, PriorityType]:
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
    
    def get_next_event(self) -> Tuple[PriorityType, EventType]:
        item = self._queue.get()
        return item.priority, item.event