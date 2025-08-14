import random
from typing import List, Tuple, Optional
from player import Player
from pokemon import Pokemon
from movedex import Move, MoveCategory, MoveType
from pokemondex import PokemonType


class BattleAction:
    """Represents an action taken in battle"""
    
    def __init__(self, player: Player, move: Move, target: Pokemon):
        self.player = player
        self.move = move
        self.target = target
        self.priority = move.priority


class TypeEffectiveness:
    """Handles type effectiveness calculations"""
    
    # Type effectiveness chart (attacker -> defender -> multiplier)
    EFFECTIVENESS = {
        MoveType.NORMAL: {PokemonType.ROCK: 0.5, PokemonType.GHOST: 0, PokemonType.STEEL: 0.5},
        MoveType.FIRE: {PokemonType.FIRE: 0.5, PokemonType.WATER: 0.5, PokemonType.GRASS: 2.0, 
                       PokemonType.ICE: 2.0, PokemonType.BUG: 2.0, PokemonType.ROCK: 0.5, 
                       PokemonType.DRAGON: 0.5, PokemonType.STEEL: 2.0},
        MoveType.WATER: {PokemonType.FIRE: 2.0, PokemonType.WATER: 0.5, PokemonType.GRASS: 0.5, 
                        PokemonType.GROUND: 2.0, PokemonType.ROCK: 2.0, PokemonType.DRAGON: 0.5},
        MoveType.ELECTRIC: {PokemonType.WATER: 2.0, PokemonType.ELECTRIC: 0.5, PokemonType.GRASS: 0.5, 
                           PokemonType.GROUND: 0, PokemonType.FLYING: 2.0, PokemonType.DRAGON: 0.5},
        MoveType.GRASS: {PokemonType.FIRE: 0.5, PokemonType.WATER: 2.0, PokemonType.GRASS: 0.5, 
                        PokemonType.POISON: 0.5, PokemonType.GROUND: 2.0, PokemonType.FLYING: 0.5, 
                        PokemonType.BUG: 0.5, PokemonType.ROCK: 2.0, PokemonType.DRAGON: 0.5, PokemonType.STEEL: 0.5},
        # Add more type matchups as needed...
    }
    
    @classmethod
    def get_effectiveness(cls, move_type: MoveType, defending_types: List[PokemonType]) -> float:
        """Calculate type effectiveness multiplier"""
        multiplier = 1.0
        
        for defending_type in defending_types:
            if move_type in cls.EFFECTIVENESS:
                type_chart = cls.EFFECTIVENESS[move_type]
                if defending_type in type_chart:
                    multiplier *= type_chart[defending_type]
        
        return multiplier


class BattleManager:
    """Manages the battle between two players"""
    
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.turn_count = 0
        self.battle_over = False
        self.winner = None
    
    def start_battle(self):
        """Start the battle and continue until one player wins"""
        print(f"\n=== BATTLE START ===")
        print(f"{self.player1.name} vs {self.player2.name}")
        
        p1_pokemon = self.player1.active_pokemon
        p2_pokemon = self.player2.active_pokemon
        if p1_pokemon and p2_pokemon:
            print(f"{p1_pokemon.species.name} vs {p2_pokemon.species.name}")
        
        while not self.battle_over:
            self.turn_count += 1
            print(f"\n--- Turn {self.turn_count} ---")
            self.execute_turn()
        
        print(f"\n=== BATTLE END ===")
        if self.winner:
            print(f"{self.winner.name} wins!")
        else:
            print("Battle ended in a draw!")
    
    def execute_turn(self):
        """Execute a single turn of battle"""
        # Check if battle should end
        if not self.player1.has_available_pokemon():
            self.battle_over = True
            self.winner = self.player2
            return
        elif not self.player2.has_available_pokemon():
            self.battle_over = True
            self.winner = self.player1
            return
        
        # Get moves from both players
        actions = []
        
        p1_active = self.player1.active_pokemon
        p2_active = self.player2.active_pokemon
        
        if p1_active and p2_active:
            move1 = self.player1.choose_move()
            if move1:
                actions.append(BattleAction(self.player1, move1, p2_active))
            
            move2 = self.player2.choose_move()
            if move2:
                actions.append(BattleAction(self.player2, move2, p1_active))
        
        # Sort actions by priority (higher priority first), then by speed
        actions.sort(key=lambda a: (a.priority, a.player.active_pokemon.speed), reverse=True)
        
        # Execute actions
        for action in actions:
            if not self.battle_over and action.player.active_pokemon and not action.player.active_pokemon.is_fainted:
                self.execute_move(action)
                
                # Check for fainted Pokemon after each move
                self.check_fainted_pokemon()
    
    def execute_move(self, action: BattleAction):
        """Execute a single move"""
        attacker = action.player.active_pokemon
        defender = action.target
        move = action.move
        
        if not attacker:
            return
        
        print(f"\n{attacker.species.name} used {move.name}!")
        
        if move.category == MoveCategory.STATUS:
            self.execute_status_move(move, attacker, defender)
        else:
            self.execute_damage_move(move, attacker, defender)
    
    def execute_damage_move(self, move: Move, attacker: Pokemon, defender: Pokemon):
        """Execute a damaging move"""
        # Check accuracy
        if random.randint(1, 100) > move.accuracy:
            print(f"{attacker.species.name}'s attack missed!")
            return
        
        # Calculate damage
        damage = self.calculate_damage(move, attacker, defender)
        
        # Apply damage
        defender.take_damage(damage)
        
        # Show effectiveness message
        effectiveness = TypeEffectiveness.get_effectiveness(move.move_type, defender.species.types)
        if effectiveness > 1.0:
            print("It's super effective!")
        elif effectiveness < 1.0 and effectiveness > 0:
            print("It's not very effective...")
        elif effectiveness == 0:
            print("It doesn't affect the defending Pokemon...")
        
        print(f"{defender.species.name} took {damage} damage! ({defender.current_hp}/{defender.max_hp} HP remaining)")
    
    def execute_status_move(self, move: Move, attacker: Pokemon, defender: Pokemon):
        """Execute a status move"""
        print(f"{move.primary_effect}")
        # Add status move effects here (stat changes, status conditions, etc.)
        
        # Example: Agility increases speed
        if move.name == "Agility":
            attacker.speed_stage = min(6, attacker.speed_stage + 2)
            print(f"{attacker.species.name}'s Speed rose sharply!")
    
    def calculate_damage(self, move: Move, attacker: Pokemon, defender: Pokemon) -> int:
        """Calculate damage dealt by a move"""
        if move.power == 0:
            return 0
        
        # Determine attack and defense stats to use
        if move.category == MoveCategory.PHYSICAL:
            attack_stat = attacker.attack
            defense_stat = defender.defense
        else:  # Special
            attack_stat = attacker.special_attack
            defense_stat = defender.special_defense
        
        # Basic damage formula (simplified)
        level_factor = (2 * attacker.level / 5 + 2)
        damage = (level_factor * move.power * attack_stat / defense_stat) / 50 + 2
        
        # Apply type effectiveness
        effectiveness = TypeEffectiveness.get_effectiveness(move.move_type, defender.species.types)
        damage *= effectiveness
        
        # Add random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)
        
        # STAB (Same Type Attack Bonus)
        if move.move_type.value in [t.value for t in attacker.species.types]:
            damage *= 1.5
        
        return max(1, int(damage))
    
    def check_fainted_pokemon(self):
        """Check for fainted Pokemon and handle switches"""
        for player in [self.player1, self.player2]:
            if player.active_pokemon and player.active_pokemon.is_fainted:
                print(f"\n{player.active_pokemon.species.name} fainted!")
                
                available = player.get_available_pokemon()
                if available:
                    print(f"\n{player.name}, choose your next Pokemon:")
                    for i, pokemon in enumerate(player.team):
                        if not pokemon.is_fainted:
                            print(f"{i + 1}. {pokemon}")
                    
                    while True:
                        try:
                            choice = input("Choose Pokemon (number): ")
                            index = int(choice) - 1
                            if player.switch_pokemon(index):
                                print(f"{player.name} sent out {player.active_pokemon.species.name}!")
                                break
                            else:
                                print("Invalid choice!")
                        except (ValueError, KeyboardInterrupt):
                            print("Invalid input!")
                else:
                    print(f"{player.name} has no more Pokemon!")
    
    def get_battle_status(self):
        """Get current battle status"""
        return {
            "turn": self.turn_count,
            "player1": str(self.player1),
            "player2": str(self.player2),
            "battle_over": self.battle_over,
            "winner": self.winner.name if self.winner else None
        }
