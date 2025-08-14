from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


class PokemonType(Enum):
    """Pokemon types"""
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


@dataclass
class BaseStats:
    """Base stats for a Pokemon species"""
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    def total(self) -> int:
        """Calculate total base stats"""
        return self.hp + self.attack + self.defense + self.special_attack + self.special_defense + self.speed


class PokemonSpecies:
    """Represents a Pokemon species with its base properties"""
    
    def __init__(self, index: int, name: str, type1: PokemonType, 
                 base_stats: BaseStats, type2: Optional[PokemonType] = None):
        self.index = index
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.base_stats = base_stats
    
    @property
    def types(self) -> List[PokemonType]:
        """Get list of types for this Pokemon"""
        types = [self.type1]
        if self.type2:
            types.append(self.type2)
        return types
    
    def __str__(self):
        type_str = f"{self.type1.value}"
        if self.type2:
            type_str += f"/{self.type2.value}"
        return f"#{self.index:03d} {self.name} ({type_str})"


class PokemonDex:
    """Database of all Pokemon species"""
    
    def __init__(self):
        self.pokemon: Dict[str, PokemonSpecies] = {}
        self.pokemon_by_index: Dict[int, PokemonSpecies] = {}
        self._initialize_pokemon()
    
    def _initialize_pokemon(self):
        """Initialize the PokemonDex with some basic Pokemon"""
        starter_pokemon = [
            PokemonSpecies(1, "Bulbasaur", PokemonType.GRASS, 
                          BaseStats(45, 49, 49, 65, 65, 45), PokemonType.POISON),
            PokemonSpecies(4, "Charmander", PokemonType.FIRE,
                          BaseStats(39, 52, 43, 60, 50, 65)),
            PokemonSpecies(7, "Squirtle", PokemonType.WATER,
                          BaseStats(44, 48, 65, 50, 64, 43)),
            PokemonSpecies(25, "Pikachu", PokemonType.ELECTRIC,
                          BaseStats(35, 55, 40, 50, 50, 90)),
            PokemonSpecies(39, "Jigglypuff", PokemonType.NORMAL,
                          BaseStats(115, 45, 20, 45, 25, 20), PokemonType.FAIRY),
            PokemonSpecies(54, "Psyduck", PokemonType.WATER,
                          BaseStats(50, 52, 48, 65, 50, 55)),
            PokemonSpecies(104, "Cubone", PokemonType.GROUND,
                          BaseStats(50, 50, 95, 40, 50, 35)),
            PokemonSpecies(133, "Eevee", PokemonType.NORMAL,
                          BaseStats(55, 55, 50, 45, 65, 55)),
        ]
        
        for pokemon in starter_pokemon:
            self.pokemon[pokemon.name] = pokemon
            self.pokemon_by_index[pokemon.index] = pokemon
    
    def get_pokemon(self, name: str) -> Optional[PokemonSpecies]:
        """Get a Pokemon species by name"""
        return self.pokemon.get(name)
    
    def get_pokemon_by_index(self, index: int) -> Optional[PokemonSpecies]:
        """Get a Pokemon species by index number"""
        return self.pokemon_by_index.get(index)
    
    def add_pokemon(self, pokemon: PokemonSpecies):
        """Add a new Pokemon species to the PokemonDex"""
        self.pokemon[pokemon.name] = pokemon
        self.pokemon_by_index[pokemon.index] = pokemon
    
    def list_pokemon(self) -> List[str]:
        """Get list of all Pokemon names"""
        return list(self.pokemon.keys())
    
    def search_by_type(self, pokemon_type: PokemonType) -> List[PokemonSpecies]:
        """Find all Pokemon of a specific type"""
        return [p for p in self.pokemon.values() if pokemon_type in p.types]
