
from dataclasses import dataclass, field

from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.state.pokestate import BattleState
from src.state.field import FieldState


'''
    Class containing all information about the current state of the game:
    - battle_state: The current state of the Pokemon teams in battle.
    - event_queue: The queue of events to be processed (TODO: could be more of a list, priority is always reassigned).
    - listener_manager: The set of all active listeners.
    - field_state: Active field hazards for each player's side.
'''
@dataclass
class GameState:
    battle_state: BattleState
    event_queue: EventQueue
    listener_manager: ListenerManager
    field_state: FieldState = field(default_factory=FieldState)