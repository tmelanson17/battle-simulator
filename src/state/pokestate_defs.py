import random

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional, List

class Status(Enum):
    NONE = 0
    POISONED = 1
    BURNED = 2
    PARALYZED = 3
    SLEEP = 4
    FROZEN = 5
    FAINTED = 6

class Type(Enum):
    NORMAL = 0
    FIRE = 1
    WATER = 2
    GRASS = 3
    ELECTRIC = 4
    ICE = 5
    FIGHTING = 6
    POISON = 7
    GROUND = 8
    FLYING = 9
    PSYCHIC = 10
    BUG = 11
    ROCK = 12
    GHOST = 13
    DRAGON = 14
    DARK = 15
    STEEL = 16
    FAIRY = 17

# Type effectiveness chart
# First axis is the attacking type
# Seconds axis is the defender type
# Expressed as a float multiplier
EFFECTIVENESS = {
    Type.NORMAL: {Type.ROCK: 0.5, Type.GHOST: 0, Type.STEEL: 0.5},
    Type.FIRE: {Type.FIRE: 0.5, Type.WATER: 0.5, Type.GRASS: 2.0, 
                    Type.ICE: 2.0, Type.BUG: 2.0, Type.ROCK: 0.5, 
                    Type.DRAGON: 0.5, Type.STEEL: 2.0},
    Type.WATER: {Type.FIRE: 2.0, Type.WATER: 0.5, Type.GRASS: 0.5, 
                    Type.GROUND: 2.0, Type.ROCK: 2.0, Type.DRAGON: 0.5},
    Type.GRASS: {Type.FIRE: 0.5, Type.WATER: 2.0, Type.GRASS: 0.5, 
                    Type.POISON: 0.5, Type.GROUND: 2.0, Type.FLYING: 0.5, 
                    Type.BUG: 0.5, Type.ROCK: 2.0, Type.DRAGON: 0.5, Type.STEEL: 0.5},
    Type.ELECTRIC: {Type.WATER: 2.0, Type.ELECTRIC: 0.5, Type.GRASS: 0.5, 
                        Type.GROUND: 0, Type.FLYING: 2.0, Type.DRAGON: 0.5},
    Type.ICE: {Type.FIRE: 0.5, Type.WATER: 0.5, Type.GRASS: 2.0, 
                Type.ICE: 0.5, Type.BUG: 1.0, Type.ROCK: 1.0, 
                Type.DRAGON: 2.0, Type.STEEL: 0.5},
    Type.FIGHTING: {Type.NORMAL: 2.0, Type.FLYING: 0.5, Type.PSYCHIC: 0.5, 
                    Type.ROCK: 2.0, Type.ICE: 2.0, Type.BUG: 1.0, 
                    Type.GHOST: 0.5, Type.DARK: 1.0, Type.STEEL: 1.0},
    Type.POISON: {Type.GRASS: 2.0, Type.POISON: 0.5, Type.GROUND: 0.5,
                  Type.STEEL: 0.0},
    Type.GROUND: {Type.FIRE: 2.0, Type.WATER: 1.0, Type.GRASS: 0.5,
                  Type.ELECTRIC: 2.0, Type.FLYING: 0.0, Type.DRAGON: 1.0,
                  Type.STEEL: 2.0},
    Type.FLYING: {Type.FIGHTING: 2.0, Type.GRASS: 2.0,
                  Type.ELECTRIC: 1.0, Type.ROCK: 0.5, Type.STEEL: 1.0},
    Type.GHOST: {Type.NORMAL: 0.0, Type.GHOST: 2.0, Type.DARK: 1.0}, 
    Type.DRAGON: {Type.DRAGON: 2.0, Type.STEEL: 0.5},
    Type.DARK: {Type.NORMAL: 1.0, Type.GHOST: 2.0, Type.DARK: 0.5},
    Type.STEEL: {Type.NORMAL: 1.0, Type.FIRE: 0.5, Type.WATER: 0.5,
                 Type.ELECTRIC: 1.0, Type.ICE: 1.0, Type.FIGHTING: 0.5,
                 Type.POISON: 1.0, Type.GROUND: 1.0, Type.FLYING: 1.0,
                 Type.PSYCHIC: 1.0, Type.BUG: 1.0, Type.ROCK: 1.0,
                 Type.GHOST: 1.0, Type.DRAGON: 1.0, Type.DARK: 1.0,
                 Type.STEEL: 1.0},
    Type.FAIRY: {Type.FIRE: 0.5, Type.FIGHTING: 2.0, Type.POISON: 0.5,
                 Type.STEEL: 0.5}
}

class Category(Enum):
    PHYSICAL = 0
    SPECIAL = 1
    STATUS = 2

@dataclass
class PokemonEffect:
    property: str
    value: str

@dataclass
class Move:
    """Represents a Pokémon move with its properties."""
    name: str
    type: Type
    power: Optional[int]
    category: Category
    accuracy: int
    pp: int
    description: str
    priority: int = 0
    target_effects: List[PokemonEffect] = field(default_factory=list)


# Do standard damage calculation
def get_effectiveness(attacking_type: Type, defending_type: Type) -> float:
    return EFFECTIVENESS.get(attacking_type, {}).get(defending_type, 1.0)

# Calculate damage dealt by a move
def calculate_damage(base_power: int, offensive_stat: int, defensive_stat: int, effective_multiplier: float, stab_multiplier: float) -> int:
    return int(base_power * (offensive_stat / defensive_stat) * effective_multiplier * stab_multiplier * random.uniform(0.85, 1.0))
