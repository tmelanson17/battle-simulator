from typing import List, Optional
from pokemon import Pokemon
from movedex import Move


class Player:
    """Represents a player in the battle"""
    
    def __init__(self, name: str, team: List[Pokemon]):
        self.name = name
        self.team = team
        self.active_pokemon_index = 0
    
    @property
    def active_pokemon(self) -> Optional[Pokemon]:
        """Get the currently active Pokemon"""
        if 0 <= self.active_pokemon_index < len(self.team):
            pokemon = self.team[self.active_pokemon_index]
            if not pokemon.is_fainted:
                return pokemon
        return None
    
    def get_available_pokemon(self) -> List[Pokemon]:
        """Get all non-fainted Pokemon"""
        return [p for p in self.team if not p.is_fainted]
    
    def switch_pokemon(self, index: int) -> bool:
        """Switch to a different Pokemon"""
        if 0 <= index < len(self.team) and not self.team[index].is_fainted:
            self.active_pokemon_index = index
            return True
        return False
    
    def has_available_pokemon(self) -> bool:
        """Check if player has any non-fainted Pokemon"""
        return len(self.get_available_pokemon()) > 0
    
    def choose_move(self) -> Optional[Move]:
        """Let player choose a move for their active Pokemon"""
        active = self.active_pokemon
        if not active or not active.moves:
            return None
        
        print(f"\n{self.name}'s {active.species.name} - Available moves:")
        for i, move in enumerate(active.moves):
            print(f"{i + 1}. {move}")
        
        while True:
            try:
                choice = input(f"Choose move for {active.species.name} (1-{len(active.moves)}): ")
                move_index = int(choice) - 1
                if 0 <= move_index < len(active.moves):
                    return active.moves[move_index]
                else:
                    print("Invalid move selection!")
            except (ValueError, KeyboardInterrupt):
                print("Invalid input!")
    
    def __str__(self):
        return f"{self.name} - {len(self.get_available_pokemon())}/{len(self.team)} Pokemon remaining"
