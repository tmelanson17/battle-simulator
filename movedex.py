from enum import Enum
from typing import Dict, List, Optional, Tuple


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


class Move:
    """Represents a Pokemon move with all its properties"""
    
    def __init__(self, name: str, move_type: MoveType, category: MoveCategory, 
                 power: int, accuracy: int, pp: int, priority: int = 0,
                 primary_effect: str = "", secondary_effect: str = ""):
        self.name = name
        self.move_type = move_type
        self.category = category
        self.power = power
        self.accuracy = accuracy
        self.pp = pp
        self.priority = priority
        self.primary_effect = primary_effect
        self.secondary_effect = secondary_effect
    
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
                 "Deals damage", "No secondary effect"),
            Move("Quick Attack", MoveType.NORMAL, MoveCategory.PHYSICAL, 40, 100, 30, 1,
                 "Deals damage", "High priority"),
            Move("Thunderbolt", MoveType.ELECTRIC, MoveCategory.SPECIAL, 90, 100, 15, 0,
                 "Deals damage", "10% chance to paralyze"),
            Move("Water Gun", MoveType.WATER, MoveCategory.SPECIAL, 40, 100, 25, 0,
                 "Deals damage", "No secondary effect"),
            Move("Ember", MoveType.FIRE, MoveCategory.SPECIAL, 40, 100, 25, 0,
                 "Deals damage", "10% chance to burn"),
            Move("Vine Whip", MoveType.GRASS, MoveCategory.PHYSICAL, 45, 100, 25, 0,
                 "Deals damage", "No secondary effect"),
            Move("Thunder Wave", MoveType.ELECTRIC, MoveCategory.STATUS, 0, 90, 20, 0,
                 "Paralyzes target", "No damage dealt"),
            Move("Agility", MoveType.PSYCHIC, MoveCategory.STATUS, 0, 100, 30, 0,
                 "Raises Speed by 2 stages", "No secondary effect"),
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
