from typing import List, Optional

from pokemon import Pokemon


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

    def get_switchable_indices(self) -> List[int]:
        return [i for i, p in enumerate(self.team) if not p.is_fainted and i != self.active_pokemon_index]
    
    def switch_pokemon(self, index: int) -> bool:
        """Switch to a different Pokemon"""
        if 0 <= index < len(self.team) and not self.team[index].is_fainted:
            self.active_pokemon_index = index
            return True
        return False
    
    def has_available_pokemon(self) -> bool:
        """Check if player has any non-fainted Pokemon"""
        return len(self.get_available_pokemon()) > 0
    
    def __str__(self):
        return f"{self.name} - {len(self.get_available_pokemon())}/{len(self.team)} Pokemon remaining"
