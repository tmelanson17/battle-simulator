from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

from src.state.pokestate import PokemonState, BattleState
from src.state.pokestate_defs import Status
from src.dex.moves import Move


class Property:
    def __init__(self, full_name: str):
        tmp = full_name.split('.')
        self.container = tmp[:-1]
        self.name = tmp[-1]
    
    # TODO: What would error messages look like, should they be improved?
    def set(self, data: Any, value: Any):
        for container in self.container:
            data = getattr(data, container)
        setattr(data, self.name, value)

StateType = TypeVar('StateType', bound=PokemonState|BattleState)
class Effect(Generic[StateType], ABC):
    @abstractmethod
    def apply(self, target: StateType):
        pass

class PokemonEffect(Effect[PokemonState]):
    property: Property

    def __init__(self, property: str, value: str):
        self.property = Property(property)
        self.value = value

    def apply(self, target: PokemonState):
        self.property.set(target, self.value)


def from_move(move: Move) -> list[PokemonEffect]:
    effects = []
    for effect in move.target_effects:
        effects.append(PokemonEffect(effect.property, effect.value))
    return effects