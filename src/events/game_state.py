
from dataclasses import dataclass

from src.events.event_queue import EventQueue
from src.events.listener import ListenerManager
from src.state.pokestate import BattleState


'''
    Class containing all information about the current state of the game:
    - battle_state: The current state of the Pokemon teams in battle.
    - event_queue: The queue of events to be processed (TODO: could be more of a list, priority is always reassigned).
    - listener_manager: The set of all active listeners.
'''
@dataclass 
class GameState:
    battle_state: BattleState
    event_queue: EventQueue
    listener_manager: ListenerManager