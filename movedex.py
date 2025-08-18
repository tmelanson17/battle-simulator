from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import random


class MoveType(Enum):
    """Pokemon move types"""
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"


class MoveCategory(Enum):
    """Move damage categories"""
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"

class Property:
    def __init__(self, full_name: str):
        self.full_name = full_name
        
    def base_object(self, data: object) -> object:
        """Get the base object for this property"""
        parts = self.full_name.split('.')
        base = data
        for part in parts[:-1]:
            if not hasattr(base, part):
                raise AttributeError(f"Property '{self.full_name}' not found in {base}")
            base = getattr(base, part, None)
        return base

    def base_property_name(self) -> str:
        """Get the base property name for this property"""
        parts = self.full_name.split('.')
        return parts[-1] if parts else self.full_name
    
    def get(self, data: object) -> Any:
        base_object = self.base_object(data)
        if not hasattr(base_object, self.base_property_name()):
            raise AttributeError(f"Property '{self.full_name}' not found in {base_object}")
        return getattr(base_object, self.base_property_name(), None)

# TODO: Move the opertor/effect/condition class into its own file.
class Operator(Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    SET = "="


class Comparator(ABC):
    @abstractmethod
    def apply(self, a: float|str, b: float|str) -> bool:
        pass

class Condition(ABC):
    @abstractmethod
    def check(self, state: object) -> bool:
        pass

@dataclass
class PropertyCondition(Condition):
    property: Property
    operator: Comparator
    value: float|str

    def check(self, state: object) -> bool:
        return self.operator.apply(self.property.get(state), self.value)

@dataclass
class RandomCondition(Condition):
    probability: float

    def check(self, state: object) -> bool:
        return random.random() < self.probability

@dataclass
class Effect:
    property: Property
    operator: Operator
    value: float|str|Property
    condition: Optional[Condition] = None

    def __post_init__(self):
        if isinstance(self.value, str) and self.operator != Operator.SET:
            raise ValueError("String values can only be used with SET operator")

    def _operate(self, target: object, base_property: str):
        base_object = self.property.base_object(target)
        base_name = self.property.base_property_name()
        if self == Operator.ADD:
            base_object.__dict__[base_name] += self.value
        elif self == Operator.SUBTRACT:
            base_object.__dict__[base_name] -= self.value
        elif self == Operator.MULTIPLY:
            base_object.__dict__[base_name] *= self.value
        elif self == Operator.DIVIDE:
            base_object.__dict__[base_name] /= self.value
        elif self == Operator.SET:
            base_object.__dict__[base_name] = self.value
        raise ValueError("Invalid operator")
    
    def apply(self, target: object):
        if self.condition and not self.condition.check(target):

class Move:
    """Represents a Pokemon move with all its properties"""
    
    def __init__(self, name: str, move_type: MoveType, category: MoveCategory, 
                 power: int, accuracy: int, pp: int, priority: int = 0,
                 primary_effect: Optional[Effect] = None, secondary_effect: Optional[Effect] = None, override_effect: Optional[Effect] = None):
        self.name = name
        self.move_type = move_type
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.pp = pp
        self.priority = priority
        self.primary_effect = primary_effect
        self.secondary_effect = secondary_effect
        self.override_effect = override_effect

    def __str__(self):
        return f"{self.name} ({self.move_type.value}/{self.category.value})"


class MoveDex:
    """Database of all Pokemon moves"""
    
    def __init__(self):
        self.moves: Dict[str, Move] = {}
        self._initialize_moves()
    
    def _initialize_moves(self):
        """Initialize the MoveDex with some basic moves"""
        basic_moves = [
            Move("Tackle", MoveType.NORMAL, MoveCategory.PHYSICAL, 40, 100, 35, 0,
                 None,None),
            Move("Quick Attack", MoveType.NORMAL, MoveCategory.PHYSICAL, 40, 100, 30, 1,
                 None, None),
            Move("Thunderbolt", MoveType.ELECTRIC, MoveCategory.SPECIAL, 90, 100, 15, 0,
                 None, Effect("target.status", Operator.SET, "PARALYZED")),
            Move("Water Gun", MoveType.WATER, MoveCategory.SPECIAL, 40, 100, 25, 0,
                 None, None),
            Move("Ember", MoveType.FIRE, MoveCategory.SPECIAL, 40, 100, 25, 0,
                 None, Effect("target.status", Operator.SET, "BURNED")),
            Move("Vine Whip", MoveType.GRASS, MoveCategory.PHYSICAL, 45, 100, 25, 0,
                 None, None),
            Move("Thunder Wave", MoveType.ELECTRIC, MoveCategory.STATUS, 0, 90, 20, 0,
                 Effect("target.status", Operator.SET, "PARALYZED"), None),
            Move("Agility", MoveType.PSYCHIC, MoveCategory.STATUS, 0, 100, 30, 0,
                 Effect("self.speed", Operator.ADD, 2), None),
        ]
        
        for move in basic_moves:
            self.moves[move.name] = move
    
    def get_move(self, name: str) -> Optional[Move]:
        """Get a move by name"""
        return self.moves.get(name)
    
    def add_move(self, move: Move):
        """Add a new move to the MoveDex"""
        self.moves[move.name] = move
    
    def list_moves(self) -> List[str]:
        """Get list of all move names"""
        return list(self.moves.keys())
