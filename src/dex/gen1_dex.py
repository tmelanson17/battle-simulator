"""
Generation 1 Pokédex data including all Pokémon species and type information.
This module provides comprehensive data for all 151 original Pokémon.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from src.state.pokestate_defs import Type


@dataclass
class PokemonInfo:
    species: str
    type1: Type
    type2: Optional[Type]
    hp: int 
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

# Complete Generation 1 Pokédex
# Format: (name, type1, type2 or None, base_stats: [HP, Attack, Defense, Special, Speed])
GEN1_POKEMON = {
    1: PokemonInfo("Bulbasaur", Type.GRASS, Type.POISON, 45, 49, 49, 65, 65, 45),
    2: PokemonInfo("Ivysaur", Type.GRASS, Type.POISON, 60, 62, 63, 80, 80, 60),
    3: PokemonInfo("Venusaur", Type.GRASS, Type.POISON, 80, 82, 83, 100, 100, 80),
    4: PokemonInfo("Charmander", Type.FIRE, None, 39, 52, 43, 50, 50, 65),
    5: PokemonInfo("Charmeleon", Type.FIRE, None, 58, 64, 58, 80, 80, 80),
    6: PokemonInfo("Charizard", Type.FIRE, Type.FLYING, 78, 84, 78, 109, 109, 100),
    7: PokemonInfo("Squirtle", Type.WATER, None, 44, 48, 65, 50, 50, 43),
    8: PokemonInfo("Wartortle", Type.WATER, None, 59, 63, 80, 65, 65, 58),
    9: PokemonInfo("Blastoise", Type.WATER, None, 79, 83, 100, 85, 85, 78),
    10: PokemonInfo("Caterpie", Type.BUG, None, 45, 30, 35, 20, 20, 45),
    11: PokemonInfo("Metapod", Type.BUG, None, 50, 20, 55, 25, 25, 30),
    12: PokemonInfo("Butterfree", Type.BUG, Type.FLYING, 60, 45, 50, 90, 70, 60),
    13: PokemonInfo("Weedle", Type.BUG, Type.POISON, 40, 35, 30, 20, 50, 40),
    14: PokemonInfo("Kakuna", Type.BUG, Type.POISON, 45, 25, 50, 25, 35, 55),
    15: PokemonInfo("Beedrill", Type.BUG, Type.POISON, 65, 90, 40, 45, 75, 100),
    16: PokemonInfo("Pidgey", Type.NORMAL, Type.FLYING, 40, 45, 40, 35, 56, 55),
    17: PokemonInfo("Pidgeotto", Type.NORMAL, Type.FLYING, 63, 60, 55, 50, 71, 71),
    18: PokemonInfo("Pidgeot", Type.NORMAL, Type.FLYING, 83, 80, 75, 70, 101, 101),
    19: PokemonInfo("Rattata", Type.NORMAL, None, 30, 56, 35, 25, 72, 72),
    20: PokemonInfo("Raticate", Type.NORMAL, None, 55, 81, 60, 50, 97, 97),
    21: PokemonInfo("Spearow", Type.NORMAL, Type.FLYING, 40, 60, 30, 31, 70, 70),
    22: PokemonInfo("Fearow", Type.NORMAL, Type.FLYING, 65, 90, 65, 61, 100, 100),
    23: PokemonInfo("Ekans", Type.POISON, None, 35, 60, 44, 40, 55, 55),
    24: PokemonInfo("Arbok", Type.POISON, None, 60, 85, 69, 65, 80, 80),
    25: PokemonInfo("Pikachu", Type.ELECTRIC, None, 35, 55, 30, 50, 90, 90),
    26: PokemonInfo("Raichu", Type.ELECTRIC, None, 60, 90, 55, 90, 110, 110),
    27: PokemonInfo("Sandshrew", Type.GROUND, None, 50, 75, 85, 30, 40, 40),
    28: PokemonInfo("Sandslash", Type.GROUND, None, 75, 100, 110, 45, 65, 65),
    29: PokemonInfo("Nidoran♀", Type.POISON, None, 55, 47, 52, 40, 41, 41),
    30: PokemonInfo("Nidorina", Type.POISON, None, 70, 62, 67, 55, 56, 56),
    31: PokemonInfo("Nidoqueen", Type.POISON, Type.GROUND, 90, 92, 87, 75, 76, 76),
    32: PokemonInfo("Nidoran♂", Type.POISON, None, 46, 57, 40, 40, 50, 50),
    33: PokemonInfo("Nidorino", Type.POISON, None, 61, 72, 57, 55, 65, 65),
    34: PokemonInfo("Nidoking", Type.POISON, Type.GROUND, 81, 102, 77, 85, 85, 85),
    35: PokemonInfo("Clefairy", Type.NORMAL, None, 70, 45, 48, 60, 35, 35),
    36: PokemonInfo("Clefable", Type.NORMAL, None, 95, 70, 73, 95, 60, 60),
    37: PokemonInfo("Vulpix", Type.FIRE, None, 38, 41, 40, 65, 65, 39),
    38: PokemonInfo("Ninetales", Type.FIRE, None, 73, 76, 75, 81, 100, 100),
    39: PokemonInfo("Jigglypuff", Type.NORMAL, None, 115, 45, 20, 25, 20, 20),
    40: PokemonInfo("Wigglytuff", Type.NORMAL, None, 140, 70, 45, 85, 45, 45),
    41: PokemonInfo("Zubat", Type.POISON, Type.FLYING, 40, 45, 35, 40, 55, 55),
    42: PokemonInfo("Golbat", Type.POISON, Type.FLYING, 75, 80, 70, 65, 90, 90),
    43: PokemonInfo("Oddish", Type.GRASS, Type.POISON, 45, 50, 55, 75, 30, 30),
    44: PokemonInfo("Gloom", Type.GRASS, Type.POISON, 60, 65, 70, 85, 40, 40),
    45: PokemonInfo("Vileplume", Type.GRASS, Type.POISON, 75, 80, 85, 110, 50, 50),
    46: PokemonInfo("Paras", Type.BUG, Type.GRASS, 35, 70, 55, 55, 25, 25),
    47: PokemonInfo("Parasect", Type.BUG, Type.GRASS, 60, 95, 80, 60, 30, 30),
    48: PokemonInfo("Venonat", Type.BUG, Type.POISON, 60, 55, 50, 40, 45, 45),
    49: PokemonInfo("Venomoth", Type.BUG, Type.POISON, 70, 65, 60, 90, 90, 90),
    50: PokemonInfo("Diglett", Type.GROUND, None, 10, 55, 25, 45, 95, 95),
    51: PokemonInfo("Dugtrio", Type.GROUND, None, 35, 80, 50, 50, 120, 120),
    52: PokemonInfo("Meowth", Type.NORMAL, None, 40, 45, 35, 40, 90, 90),
    53: PokemonInfo("Persian", Type.NORMAL, None, 65, 70, 60, 65, 115, 115),
    54: PokemonInfo("Psyduck", Type.WATER, None, 50, 52, 48, 50, 55, 55),
    55: PokemonInfo("Golduck", Type.WATER, None, 80, 82, 78, 95, 85, 85),
    56: PokemonInfo("Mankey", Type.FIGHTING, None, 40, 80, 35, 35, 70, 70),
    57: PokemonInfo("Primeape", Type.FIGHTING, None, 65, 105, 60, 60, 95, 95),
    58: PokemonInfo("Growlithe", Type.FIRE, None, 55, 70, 45, 50, 60, 60),
    59: PokemonInfo("Arcanine", Type.FIRE, None, 90, 110, 80, 100, 95, 95),
    60: PokemonInfo("Poliwag", Type.WATER, None, 40, 50, 40, 40, 90, 90),
    61: PokemonInfo("Poliwhirl", Type.WATER, None, 65, 65, 65, 50, 90, 90),
    62: PokemonInfo("Poliwrath", Type.WATER, Type.FIGHTING, 90, 95, 95, 70, 70, 70),
    63: PokemonInfo("Abra", Type.PSYCHIC, None, 25, 20, 15, 105, 90, 90),
    64: PokemonInfo("Kadabra", Type.PSYCHIC, None, 40, 35, 30, 120, 105, 105),
    65: PokemonInfo("Alakazam", Type.PSYCHIC, None, 55, 50, 45, 135, 120, 120),
    66: PokemonInfo("Machop", Type.FIGHTING, None, 70, 80, 50, 35, 35, 35),
    67: PokemonInfo("Machoke", Type.FIGHTING, None, 80, 100, 70, 50, 45, 45),
    68: PokemonInfo("Machamp", Type.FIGHTING, None, 90, 130, 80, 65, 55, 55),
    69: PokemonInfo("Bellsprout", Type.GRASS, Type.POISON, 50, 75, 35, 70, 40, 40),
    70: PokemonInfo("Weepinbell", Type.GRASS, Type.POISON, 65, 90, 50, 85, 55, 55),
    71: PokemonInfo("Victreebel", Type.GRASS, Type.POISON, 80, 105, 65, 100, 70, 70),
    72: PokemonInfo("Tentacool", Type.WATER, Type.POISON, 40, 40, 35, 50, 70, 70),
    73: PokemonInfo("Tentacruel", Type.WATER, Type.POISON, 80, 70, 65, 80, 100, 100),
    74: PokemonInfo("Geodude", Type.ROCK, Type.GROUND, 40, 80, 100, 30, 20, 20),
    75: PokemonInfo("Graveler", Type.ROCK, Type.GROUND, 55, 95, 115, 45, 35, 35),
    76: PokemonInfo("Golem", Type.ROCK, Type.GROUND, 80, 120, 130, 55, 45, 45),
    77: PokemonInfo("Ponyta", Type.FIRE, None, 50, 85, 55, 65, 90, 90),
    78: PokemonInfo("Rapidash", Type.FIRE, None, 65, 100, 70, 80, 105, 105),
    79: PokemonInfo("Slowpoke", Type.WATER, Type.PSYCHIC, 90, 65, 65, 40, 15, 15),
    80: PokemonInfo("Slowbro", Type.WATER, Type.PSYCHIC, 95, 75, 110, 100, 30, 30),
    81: PokemonInfo("Magnemite", Type.ELECTRIC, None, 25, 35, 70, 95, 45, 45),
    82: PokemonInfo("Magneton", Type.ELECTRIC, None, 50, 60, 95, 120, 70, 70),
    83: PokemonInfo("Farfetch'd", Type.NORMAL, Type.FLYING, 52, 65, 55, 58, 60, 60),
    84: PokemonInfo("Doduo", Type.NORMAL, Type.FLYING, 35, 85, 45, 35, 75, 75),
    85: PokemonInfo("Dodrio", Type.NORMAL, Type.FLYING, 60, 110, 70, 60, 100, 100),
    86: PokemonInfo("Seel", Type.WATER, None, 65, 45, 55, 45, 45, 45),
    87: PokemonInfo("Dewgong", Type.WATER, Type.ICE, 90, 70, 80, 70, 70, 70),
    88: PokemonInfo("Grimer", Type.POISON, None, 80, 80, 50, 40, 25, 25),
    89: PokemonInfo("Muk", Type.POISON, None, 105, 105, 75, 65, 50, 50),
    90: PokemonInfo("Shellder", Type.WATER, None, 30, 65, 100, 45, 40, 40),
    91: PokemonInfo("Cloyster", Type.WATER, Type.ICE, 50, 95, 180, 85, 70, 70),
    92: PokemonInfo("Gastly", Type.GHOST, Type.POISON, 30, 35, 30, 100, 80, 80),
    93: PokemonInfo("Haunter", Type.GHOST, Type.POISON, 45, 50, 45, 115, 95, 95),
    94: PokemonInfo("Gengar", Type.GHOST, Type.POISON, 60, 65, 60, 130, 110, 110),
    95: PokemonInfo("Onix", Type.ROCK, Type.GROUND, 35, 45, 160, 30, 70, 70),
    96: PokemonInfo("Drowzee", Type.PSYCHIC, None, 60, 48, 45, 43, 42, 42),
    97: PokemonInfo("Hypno", Type.PSYCHIC, None, 85, 73, 70, 73, 67, 67),
    98: PokemonInfo("Krabby", Type.WATER, None, 30, 105, 90, 25, 50, 50),
    99: PokemonInfo("Kingler", Type.WATER, None, 55, 130, 115, 50, 75, 75),
    100:PokemonInfo("Voltorb", Type.ELECTRIC, None, 40, 30, 50, 55, 100, 100),
    101:PokemonInfo("Electrode", Type.ELECTRIC, None, 60, 50, 70, 80, 140, 140),
    102:PokemonInfo("Exeggcute", Type.GRASS, Type.PSYCHIC, 60, 40, 80, 60, 40, 40),
    103:PokemonInfo("Exeggutor", Type.GRASS, Type.PSYCHIC, 95, 95, 85, 125, 55, 55),
    104:PokemonInfo("Cubone", Type.GROUND, None, 50, 50, 95, 40, 35, 35),
    105:PokemonInfo("Marowak", Type.GROUND, None, 60, 80, 110, 50, 45, 45),
    106:PokemonInfo("Hitmonlee", Type.FIGHTING, None, 50, 120, 53, 35, 87, 87),
    107:PokemonInfo("Hitmonchan", Type.FIGHTING, None, 50, 105, 79, 35, 76, 76),
    108:PokemonInfo("Lickitung", Type.NORMAL, None, 90, 55, 75, 60, 60, 30),
    109:PokemonInfo("Koffing", Type.POISON, None, 40, 65, 95, 60, 60, 35),
    110:PokemonInfo("Weezing", Type.POISON, None, 65, 90, 120, 85, 85, 60),
    111:PokemonInfo("Rhyhorn", Type.GROUND, Type.ROCK, 80, 85, 95, 30, 30, 25),
    112:PokemonInfo("Rhydon", Type.GROUND, Type.ROCK, 105, 130, 120, 45, 45, 40),
    113:PokemonInfo("Chansey", Type.NORMAL, None, 250, 5, 5, 35, 35, 50),
    114:PokemonInfo("Tangela", Type.GRASS, None, 65, 55, 115, 100, 100, 60),
    115:PokemonInfo("Kangaskhan", Type.NORMAL, None, 105, 95, 80, 40, 40, 90),
    116:PokemonInfo("Horsea", Type.WATER, None, 30, 40, 70, 70, 70, 60),
    117:PokemonInfo("Seadra", Type.WATER, None, 55, 65, 95, 95, 95, 85),
    118:PokemonInfo("Goldeen", Type.WATER, None, 45, 67, 60, 50, 50, 63),
    119:PokemonInfo("Seaking", Type.WATER, None, 80, 92, 65, 65, 65, 68),
    120:PokemonInfo("Staryu", Type.WATER, None, 30, 45, 55, 70, 70, 85),
    121:PokemonInfo("Starmie", Type.WATER, Type.PSYCHIC, 60, 75, 85, 100, 100, 115),
    122:PokemonInfo("Mr. Mime", Type.PSYCHIC, None, 40, 45, 65, 100, 100, 90),
    123:PokemonInfo("Scyther", Type.BUG, Type.FLYING, 70, 110, 80, 55, 55, 105),
    124:PokemonInfo("Jynx", Type.ICE, Type.PSYCHIC, 65, 50, 35, 115, 115, 95),
    125:PokemonInfo("Electabuzz", Type.ELECTRIC, None, 65, 83, 57, 95, 95, 105),
    126:PokemonInfo("Magmar", Type.FIRE, None, 65, 95, 57, 100, 100, 93),
    127:PokemonInfo("Pinsir", Type.BUG, None, 65, 125, 100, 55, 55, 85),
    128:PokemonInfo("Tauros", Type.NORMAL, None, 75, 100, 95, 40, 40, 110),
    129:PokemonInfo("Magikarp", Type.WATER, None, 20, 10, 55, 20, 20, 80),
    130:PokemonInfo("Gyarados", Type.WATER, Type.FLYING, 95, 125, 79, 60, 60, 81),
    131:PokemonInfo("Lapras", Type.WATER, Type.ICE, 130, 85, 80, 85, 85, 60),
    132:PokemonInfo("Ditto", Type.NORMAL, None, 48, 48, 48, 48, 48, 48),
    133:PokemonInfo("Eevee", Type.NORMAL, None, 55, 55, 50, 65, 65, 55),
    134:PokemonInfo("Vaporeon", Type.WATER, None, 130, 65, 60, 110, 110, 65),
    135:PokemonInfo("Jolteon", Type.ELECTRIC, None, 65, 65, 60, 110, 110, 130),
    136:PokemonInfo("Flareon", Type.FIRE, None, 65, 130, 60, 95, 95, 65),
    137:PokemonInfo("Porygon", Type.NORMAL, None, 65, 60, 70, 85, 85, 40),
    138:PokemonInfo("Omanyte", Type.ROCK, Type.WATER, 35, 40, 100, 90, 90, 35),
    139:PokemonInfo("Omastar", Type.ROCK, Type.WATER, 70, 60, 125, 115, 115, 55),
    140:PokemonInfo("Kabuto", Type.ROCK, Type.WATER, 30, 80, 90, 45, 45, 55),
    141:PokemonInfo("Kabutops", Type.ROCK, Type.WATER, 60, 115, 105, 65, 65, 80),
    142:PokemonInfo("Aerodactyl", Type.ROCK, Type.FLYING, 80, 105, 65, 60, 60, 130),
    143:PokemonInfo("Snorlax", Type.NORMAL, None, 160, 110, 65, 65, 65, 30),
    144:PokemonInfo("Articuno", Type.ICE, Type.FLYING, 90, 85, 100, 95, 95, 85),
    145:PokemonInfo("Zapdos", Type.ELECTRIC, Type.FLYING, 90, 90, 85, 125, 125, 100),
    146:PokemonInfo("Moltres", Type.FIRE, Type.FLYING, 90, 100, 90, 125, 125, 90),
    147:PokemonInfo("Dratini", Type.DRAGON, None, 41, 64, 45, 50, 50, 50),
    148:PokemonInfo("Dragonair", Type.DRAGON, None, 61, 84, 65, 70, 70, 70),
    149:PokemonInfo("Dragonite", Type.DRAGON, Type.FLYING, 91, 134, 95, 100, 100, 80),
    150:PokemonInfo("Mewtwo", Type.PSYCHIC, None, 106, 110, 90, 154, 154, 130),
    151:PokemonInfo("Mew", Type.PSYCHIC, None, 100, 100, 100, 100, 100, 100),
}

# Petit Cup eligible Pokémon (unevolved, max 6'08" tall, max 44lbs weight)
# Based on Pokémon Stadium Petit Cup rules
PC_ELIGIBLE = [
    1,   # Bulbasaur
    4,   # Charmander  
    7,   # Squirtle
    10,  # Caterpie
    13,  # Weedle
    16,  # Pidgey
    19,  # Rattata
    21,  # Spearow
    23,  # Ekans
    25,  # Pikachu
    27,  # Sandshrew
    29,  # Nidoran♀
    32,  # Nidoran♂
    35,  # Clefairy
    37,  # Vulpix
    39,  # Jigglypuff
    41,  # Zubat
    43,  # Oddish
    46,  # Paras
    50,  # Diglett
    52,  # Meowth
    54,  # Psyduck
    58,  # Growlithe
    60,  # Poliwag
    63,  # Abra
    66,  # Machop
    69,  # Bellsprout
    74,  # Geodude
    81,  # Magnemite
    83,  # Farfetch'd
    90,  # Shellder
    92,  # Gastly
    98,  # Krabby
    100, # Voltorb
    102, # Exeggcute
    104, # Cubone
    109, # Koffing
    116, # Horsea
    118, # Goldeen
    129, # Magikarp
    132, # Ditto
    133, # Eevee
    138, # Omanyte
    140, # Kabuto
    147, # Dratini
]


def get_pokemon_by_dex_number(dex_num: int) -> PokemonInfo:
    """Get Pokémon data by Pokédex number."""
    if dex_num not in GEN1_POKEMON:
        raise ValueError(f"Invalid Pokédex number: {dex_num}")
    
    return GEN1_POKEMON[dex_num]


def get_pokemon_by_name(name: str) -> PokemonInfo:
    """Get Pokémon data by name."""
    for _, pokemon in GEN1_POKEMON.items():
        if pokemon.species.lower() == name.lower():
            return pokemon

    raise ValueError(f"Pokémon not found: {name}")


def is_pc_eligible(dex_num: int) -> bool:
    """Check if a Pokémon is eligible for Petit Cup."""
    return dex_num in PC_ELIGIBLE


def get_all_pc_pokemon() -> List[Tuple[int, str, Type, Optional[Type], List[int]]]:
    """Get all Petit Cup eligible Pokémon."""
    pc_pokemon = []
    for dex_num in PC_ELIGIBLE:
        pokemon = GEN1_POKEMON[dex_num]
        stats = [pokemon.hp, pokemon.attack, pokemon.defense, pokemon.special_attack, pokemon.special_defense, pokemon.speed]
        pc_pokemon.append((dex_num, pokemon.species, pokemon.type1, pokemon.type2, stats))
    
    return pc_pokemon


def get_pokemon_by_type(poke_type: Type) -> List[Tuple[int, str, Type, Optional[Type], List[int]]]:
    """Get all Pokémon that have the specified type."""
    result = []
    for dex_num, pokemon in GEN1_POKEMON.items():
        if pokemon.type1 == poke_type or pokemon.type2 == poke_type:
            stats = [pokemon.hp, pokemon.attack, pokemon.defense, pokemon.special_attack, pokemon.special_defense, pokemon.speed]
            result.append((dex_num, pokemon.species, pokemon.type1, pokemon.type2, stats))
    
    return result

def get_species_index_by_name(name: str) -> int:
    """Get the Pokédex index by Pokémon name."""
    for dex_num, pokemon in GEN1_POKEMON.items():
        if pokemon.species.lower() == name.lower():
            return dex_num
    raise ValueError(f"Pokémon not found: {name}")

def get_species_name_by_index(idx: int) -> str:
    if idx not in GEN1_POKEMON:
        raise ValueError(f"Invalid Pokédex index: {idx}")
    return GEN1_POKEMON[idx].species

def get_type_index_by_name(name: str) -> int:
    for i, type_enum in enumerate(Type):
        if type_enum.name.lower() == name.lower():
            return i
    raise ValueError(f"Invalid typename: {name}")

def get_type_name_by_index(idx: int) -> str:
    types_list = list(Type)
    if idx < 0 or idx >= len(types_list):
        raise ValueError(f"Invalid type index: {idx}")
    return types_list[idx].name

if __name__ == "__main__":
    # Example usage
    print("Generation 1 Pokédex Demo")
    print("=" * 30)
    
    # Show all types
    print(f"Types: {', '.join([t.name for t in Type])}")
    print()
    
    # Show a few Pokémon
    for dex_num in [1, 25, 150]:
        pokemon = get_pokemon_by_dex_number(dex_num)
        type_str = f"{pokemon.type1.name}/{pokemon.type2.name}" if pokemon.type2 else pokemon.type1.name
        print(f"#{dex_num:03d} {pokemon.species} ({type_str}) - Stats: {pokemon.hp}/{pokemon.attack}/{pokemon.defense}/{pokemon.special_attack}/{pokemon.special_defense}/{pokemon.speed}")

    print()
    print(f"Petit Cup eligible Pokémon: {len(PC_ELIGIBLE)}")
    print("First 10 PC Pokémon:")
    for i, dex_num in enumerate(PC_ELIGIBLE[:10]):
        pokemon = get_pokemon_by_dex_number(dex_num)
        type_str = f"{pokemon.type1.name}/{pokemon.type2.name}" if pokemon.type2 else pokemon.type1.name
        print(f"  #{dex_num:03d} {pokemon.species} ({type_str})")
