from typing import List, Optional
from pokemondex import PokemonSpecies, BaseStats
from movedex import Move


class Pokemon:
    """Represents an individual Pokemon instance in battle"""
    
    def __init__(self, species: PokemonSpecies, level: int = 50, 
                 moves: Optional[List[Move]] = None):
        self.species = species
        self.level = level
        self.moves = moves or []
        self.current_hp = self.max_hp
        self.status = None  # Future: paralysis, burn, sleep, etc.
        
        # Battle stats (can be modified by moves/abilities)
        self.attack_stage = 0
        self.defense_stage = 0
        self.special_attack_stage = 0
        self.special_defense_stage = 0
        self.speed_stage = 0
    
    @property
    def max_hp(self) -> int:
        """Calculate max HP based on base stats and level"""
        base_hp = self.species.base_stats.hp
        return int(((2 * base_hp * self.level) / 100) + self.level + 10)
    
    @property
    def attack(self) -> int:
        """Calculate current attack stat"""
        base_stat = self.species.base_stats.attack
        stat = int(((2 * base_stat * self.level) / 100) + 5)
        return self._apply_stage_modifier(stat, self.attack_stage)
    
    @property
    def defense(self) -> int:
        """Calculate current defense stat"""
        base_stat = self.species.base_stats.defense
        stat = int(((2 * base_stat * self.level) / 100) + 5)
        return self._apply_stage_modifier(stat, self.defense_stage)
    
    @property
    def special_attack(self) -> int:
        """Calculate current special attack stat"""
        base_stat = self.species.base_stats.special_attack
        stat = int(((2 * base_stat * self.level) / 100) + 5)
        return self._apply_stage_modifier(stat, self.special_attack_stage)
    
    @property
    def special_defense(self) -> int:
        """Calculate current special defense stat"""
        base_stat = self.species.base_stats.special_defense
        stat = int(((2 * base_stat * self.level) / 100) + 5)
        return self._apply_stage_modifier(stat, self.special_defense_stage)
    
    @property
    def speed(self) -> int:
        """Calculate current speed stat"""
        base_stat = self.species.base_stats.speed
        stat = int(((2 * base_stat * self.level) / 100) + 5)
        return self._apply_stage_modifier(stat, self.speed_stage)
    
    def _apply_stage_modifier(self, base_stat: int, stage: int) -> int:
        """Apply stat stage modifiers (-6 to +6)"""
        if stage == 0:
            return base_stat
        elif stage > 0:
            return int(base_stat * (2 + stage) / 2)
        else:
            return int(base_stat * 2 / (2 - stage))
    
    @property
    def is_fainted(self) -> bool:
        """Check if Pokemon has fainted"""
        return self.current_hp <= 0
    
    def take_damage(self, damage: int):
        """Apply damage to Pokemon"""
        self.current_hp = max(0, self.current_hp - damage)
    
    def heal(self, amount: int):
        """Heal Pokemon by specified amount"""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def add_move(self, move: Move):
        """Add a move to this Pokemon's moveset (max 4 moves)"""
        if len(self.moves) < 4:
            self.moves.append(move)
        else:
            raise ValueError("Pokemon can only have 4 moves")
    
    def __str__(self):
        return f"{self.species.name} (Lv.{self.level}) - {self.current_hp}/{self.max_hp} HP"
