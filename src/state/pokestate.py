from dataclasses import dataclass, field
import enum
from typing import Optional, List, Tuple

import src.dex.moves as moves
import src.dex.gen1_dex as dex
from src.state.pokestate_defs import Move, Status, Type, Category

@dataclass
class MoveState:
    known : bool
    name : str
    pp : int
    pp_max : int
    disabled : bool
    move_info : Optional[Move] = field(default=None, repr=False)

    @property
    def available(self):
        return self.pp > 0 and not self.disabled

    @staticmethod
    def from_dex(move_arg: Move|str) -> 'MoveState':
        move: Optional[Move] = None
        if isinstance(move_arg, Move):
            move = move_arg
        elif isinstance(move_arg, str):
            move = moves.get_move_by_name(move_arg)
            if move is None:
                raise ValueError(f"Move '{move_arg}' not found")
        return MoveState(
            known=False,
            name=move.name,
            pp=move.pp,
            pp_max=move.pp,
            disabled=False,
            move_info=move
        )


@dataclass
class Stat:
    _base: int = 0
    _boost: int = 0

    BOOST_UNIT = 0.5
    MAX_BOOSTS = 6

    @property
    def current_stat(self) -> int:
        if self._boost < 0:
            return int(self._base * (1 / (1 + self._boost*self.BOOST_UNIT)))
        else:
            return int(self._base * (1 + self._boost * self.BOOST_UNIT))

    @property 
    def base(self) -> int:
        return self._base

    @base.setter
    def base(self, value: int):
        if value < 0:
            raise ValueError("Base stat cannot be negative")
        self._base = value

    def __int__(self):
        return self.current_stat

    def boost(self, amount: int) -> bool:
        if self._boost == -self.MAX_BOOSTS or self._boost == self.MAX_BOOSTS:
            return False
        self._boost = min(max(self._boost + amount, -self.MAX_BOOSTS), self.MAX_BOOSTS)
        return True

    @staticmethod
    def from_value(value: int):
        stat = Stat()
        stat.base = value
        return stat

@dataclass
class PokemonState:
    active: bool = False # Whether the pokemon is currently active in battle
    known: bool = False # Whether the Pokemon in this slot is known to the opponent
    revealed: bool = False # Whether the Pokemon in this slot has been revealed to the opponent
    in_play: bool = False # True if brought to the battle
    level: int = 100 # Level of the Pokemon

    # TODO: Convert to % when encoding for AI
    _hp: int = 0 # Current HP of the Pokemon 
    hp_max: int = 0 # Max HP of the Pokemon
    attack: Stat = field(default_factory=lambda: Stat.from_value(100)) # Attack stat of the Pokemon
    defense: Stat = field(default_factory=lambda: Stat.from_value(100)) # Defense stat of the Pokemon
    special_attack: Stat = field(default_factory=lambda: Stat.from_value(100)) # Special Attack stat of the Pokemon
    special_defense: Stat = field(default_factory=lambda: Stat.from_value(100)) # Special Defense stat of the Pokemon
    speed: Stat = field(default_factory=lambda: Stat.from_value(100)) # Speed stat of the Pokemon

    name: Optional[str] = None # Nickname
    species: Optional[str] = None # Species name
    type1: Optional[Type] = None # Species type 1,2
    type2: Optional[Type] = None
    status: Status = Status.NONE # Status condition of the Pokemon
    trapped: bool = False # Volatile conditions (listed one at a time)
    two_turn_move: bool = False # Whether the Pokemon is currently using a two-turn move
    confused: bool = False # Whether the Pokemon is currently confused
    sleep_turns: int = 0 # Number of turns asleep (0 if not asleep)
    substitute : bool = False # Whether the Pokemon has a substitute active
    reflect: bool = False # Gen 1 reflect
    light_screen: bool = False # Gen 1 light screen
    moves: List[MoveState] = field(default_factory=list)

    def __init__(self, name: str, level: int, moves: List[str]):
        pokemon = dex.get_pokemon_by_name(name)
        self.name = name
        self.level = level
        self.moves = [MoveState.from_dex(move_name) for move_name in moves]
        if pokemon:
            self.species = pokemon.species
            self.type1 = pokemon.type1
            self.type2 = pokemon.type2
            self.hp_max = pokemon.hp
            self._hp = self.hp_max
            self.attack = Stat.from_value(pokemon.attack)
            self.defense = Stat.from_value(pokemon.defense)
            self.special_attack = Stat.from_value(pokemon.special_attack)
            self.special_defense = Stat.from_value(pokemon.special_defense)
            self.speed = Stat.from_value(pokemon.speed)

    @property
    def hp(self) -> int:
        return self._hp 

    def hp_percent(self) -> float:
        return self._hp / self.hp_max * 100 if self.hp_max > 0 else 0.0

    @hp.setter
    def hp(self, value: int):
        self._hp = max(0, min(value, self.hp_max))
        if self._hp == 0:
            self.status = Status.FAINTED
        elif self.status == Status.FAINTED:
            self.status = Status.NONE
    
    @property
    def fainted(self) -> bool:
        return self.status == Status.FAINTED

    def valid_move(self, move_idx: int) -> bool:
        if move_idx < 0 or move_idx >= len(self.moves):
            return False
        return self.moves[move_idx].available

    def get_offensive_stat(self, category: Category) -> int:
        if category == Category.PHYSICAL:
            return self.attack.current_stat
        elif category == Category.SPECIAL:
            return self.special_attack.current_stat
        else:
            raise ValueError(f"Unknown move category: {category}")
    
    def get_defensive_stat(self, category: Category) -> int:
        if category == Category.PHYSICAL:
            return self.defense.current_stat
        elif category == Category.SPECIAL:
            return self.special_defense.current_stat
        else:
            raise ValueError(f"Unknown move category: {category}")
    

class Player(enum.Enum):
    PLAYER_1 = 1
    PLAYER_2 = 2

@dataclass
class PlayerState:
    # List of Pokemon brought to the battle
    pk_list: List[PokemonState]

    # List of indices of Pokemon chosen in team preview, in the order they were selected
    in_play: List[int] 

    # Current active Pokemon
    active_mons: List[int]

    def get_available_pokemon(self) -> List[Tuple[int, PokemonState]]:
        return [(i, self.pk_list[i]) for i in self.in_play if not self.pk_list[i].status == Status.FAINTED and i not in self.active_mons]

    def get_active_mon(self, slot: int = 0) -> PokemonState:
        if slot < 0 or slot >= len(self.active_mons):
            raise IndexError(f"Active slot {slot} out of range for active mons {self.active_mons}")
        return self.pk_list[self.active_mons[slot]]
    
    def is_finished(self) -> bool:
        return all(self.pk_list[i].fainted for i in self.in_play)

    def switch_pokemon(self, slot_idx: int, new_idx: int):
        if new_idx < 0 or new_idx >= len(self.pk_list):
            raise IndexError(f"New index {new_idx} out of range for Pokemon list")
        if slot_idx < 0 or slot_idx >= len(self.active_mons):
            raise IndexError(f"Slot index {slot_idx} out of range for active mons {self.active_mons}")
        self.active_mons[slot_idx] = new_idx

@dataclass
class BattleState:
    player_1: PlayerState
    player_2: PlayerState
    turn_count: int = 0

    def get_player(self, player_id: Player) -> PlayerState:
        if player_id == Player.PLAYER_1:
            return self.player_1
        elif player_id == Player.PLAYER_2:
            return self.player_2
        else:
            raise ValueError("Invalid player ID")
        
    def get_opponent(self, player_id: Player) -> PlayerState:
        if player_id == Player.PLAYER_1:
            return self.player_2
        elif player_id == Player.PLAYER_2:
            return self.player_1
        else:
            raise ValueError("Invalid player ID")
    
    def is_finished(self) -> bool:
        return self.player_1.is_finished() or self.player_2.is_finished()


def print_battle_state(battle_state: BattleState, title: str = "Battle State") -> None:
    """
    Print the BattleState in a clear, formatted way for debugging and visualization.
    
    Args:
        battle_state: The BattleState to print
        title: Optional title for the printout
    """
    print("=" * 80)
    print(f"{title:^80}")
    print("=" * 80)
    
    def print_pokemon(pokemon: PokemonState, slot: int, is_active: bool = False) -> None:
        """Helper function to print a single Pokemon's state"""
        status_indicator = "🔴" if is_active else "⚪"
        species_name = pokemon.species or "Unknown"
        level_str = f"Lv.{pokemon.level}" if pokemon.level > 0 else "Lv.?"

        # Format HP with one decimal place, ensuring one digit before the decimal
        hp_str = f"{pokemon.hp:d}/{pokemon.hp_max:d} ({pokemon.hp / pokemon.hp_max * 100:.1f}%)" if pokemon.hp > 0 else "0.0%"
        
        # Status condition emoji
        status_emoji = {
            Status.NONE: "",
            Status.BURNED: "🔥",
            Status.FROZEN: "🧊", 
            Status.PARALYZED: "⚡",
            Status.POISONED: "☠️",
            Status.SLEEP: "💤",
            Status.FAINTED: "💀"
        }.get(pokemon.status, "")
        
        print(f"  {status_indicator} Slot {slot+1}: {species_name} {level_str} - HP: {hp_str} {status_emoji}")

        if pokemon.known and pokemon.moves:
            moves = []
            for move in pokemon.moves:
                if move and move.known and move.name:
                    pp_str = f"({move.pp}/{move.pp_max})"
                    disabled_str = " [DISABLED]" if move.disabled else ""
                    moves.append(f"{move.name} {pp_str}{disabled_str}")
            if moves:
                print(f"    Moves: {' | '.join(moves)}")
        
        # Show stats
        stats = []
        stats.append(f"Atk: {pokemon.attack.current_stat:d}")
        stats.append(f"Def: {pokemon.defense.current_stat:d}")
        stats.append(f"SpcA: {pokemon.special_attack.current_stat:d}")
        stats.append(f"SpcD: {pokemon.special_defense.current_stat:d}")
        stats.append(f"Spd: {pokemon.speed.current_stat:d}")
        if stats:
            print(f"    Current Stats: {' | '.join(stats)}")
            
        # Show conditions
        conditions = []
        if pokemon.trapped:
            conditions.append("Trapped")
        if pokemon.confused:
            conditions.append("Confused")
        if pokemon.substitute:
            conditions.append("Substitute")
        if pokemon.reflect:
            conditions.append("Reflect")
        if pokemon.light_screen:
            conditions.append("Light Screen")
        if pokemon.two_turn_move:
            conditions.append("Two-turn Move")
        if pokemon.sleep_turns > 0:
            conditions.append(f"Sleep ({pokemon.sleep_turns} turns)")
        if conditions:
            print(f"    Conditions: {' | '.join(conditions)}")
    
    # Player team
    print("\n🔵 PLAYER TEAM:")
    print("-" * 40)
    for i, pokemon in enumerate(battle_state.player_1.pk_list):
        is_active = (i == battle_state.player_1.active_mons[0])
        print_pokemon(pokemon, i, is_active)
    
    # Opponent team  
    print("\n🔴 OPPONENT TEAM:")
    print("-" * 40)
    for i, pokemon in enumerate(battle_state.player_2.pk_list):
        is_active = (i == battle_state.player_2.active_mons[0])
        print_pokemon(pokemon, i, is_active)
    
    print("\n" + "=" * 80)

# Creates a default battle state with empty teams and active Pokemon in the first slot.
def create_default_battle_state(team_1: List[str], team_2: List[str], moves_1: List[List[str]], moves_2: List[List[str]]) -> BattleState:
    return BattleState(
        player_1=PlayerState(in_play=[i for i in range(len(team_1))], 
                             pk_list=[PokemonState(name=name, level=100, moves=moves) for moves, name in zip(moves_1,team_1)], active_mons=[0]),
        player_2=PlayerState(in_play=[i for i in range(len(team_2))], 
                             pk_list=[PokemonState(name=name, level=100, moves=moves) for moves, name in zip(moves_2, team_2)], active_mons=[0])
    )

if __name__ == "__main__":
    state = create_default_battle_state(
        ["Pikachu", "Bulbasaur", "Charmander"], 
        ["Squirtle", "Pidgey", "Rattata"],
        [
            ["Thunderbolt", "Quick Attack", "Seismic Toss"],
            ["Vine Whip", "Tackle", "Razor Leaf"],
            ["Ember", "Scratch", "Growl"],
        ],
        [
            ["Water Gun", "Tackle", "Bubble"],
            ["Quick Attack", "Gust", "Sand Attack"],
            ["Quick Attack", "Tackle", "Tail Whip"]
        ]
    )
    print_battle_state(state, "Default Battle State")

    print_battle_state(state, "Example Battle State")