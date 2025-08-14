#!/usr/bin/env python3
"""
Pokemon Battle Simulator
A Python application that simulates Pokemon battles with MoveDex, PokemonDex, and BattleManager.
"""

from pokemondex import PokemonDex, PokemonSpecies
from movedex import MoveDex, Move
from pokemon import Pokemon
from player import Player
from battle_manager import BattleManager


def create_sample_team(pokedex: PokemonDex, movedex: MoveDex, pokemon_names: list) -> list:
    """Create a sample team of Pokemon with moves"""
    team = []
    
    for name in pokemon_names:
        species = pokedex.get_pokemon(name)
        if species:
            pokemon = Pokemon(species, level=50)
            
            # Add some moves based on the Pokemon type
            if name == "Pikachu":
                moves_to_add = ["Thunderbolt", "Quick Attack", "Thunder Wave", "Agility"]
                for move_name in moves_to_add:
                    move = movedex.get_move(move_name)
                    if move:
                        pokemon.add_move(move)
            elif name == "Charmander":
                moves_to_add = ["Ember", "Tackle", "Quick Attack"]
                for move_name in moves_to_add:
                    move = movedex.get_move(move_name)
                    if move:
                        pokemon.add_move(move)
            elif name == "Squirtle":
                moves_to_add = ["Water Gun", "Tackle", "Quick Attack"]
                for move_name in moves_to_add:
                    move = movedex.get_move(move_name)
                    if move:
                        pokemon.add_move(move)
            elif name == "Bulbasaur":
                moves_to_add = ["Vine Whip", "Tackle", "Quick Attack"]
                for move_name in moves_to_add:
                    move = movedex.get_move(move_name)
                    if move:
                        pokemon.add_move(move)
            else:
                # Default moveset
                moves_to_add = ["Tackle", "Quick Attack"]
                for move_name in moves_to_add:
                    move = movedex.get_move(move_name)
                    if move:
                        pokemon.add_move(move)
            
            team.append(pokemon)
    
    return team


def display_pokemon_info(pokemon: Pokemon):
    """Display detailed information about a Pokemon"""
    print(f"\n{pokemon.species.name} (Level {pokemon.level})")
    print(f"Type: {'/'.join([t.value for t in pokemon.species.types])}")
    print(f"HP: {pokemon.current_hp}/{pokemon.max_hp}")
    print(f"Attack: {pokemon.attack}")
    print(f"Defense: {pokemon.defense}")
    print(f"Sp. Attack: {pokemon.special_attack}")
    print(f"Sp. Defense: {pokemon.special_defense}")
    print(f"Speed: {pokemon.speed}")
    print(f"Moves: {', '.join([move.name for move in pokemon.moves])}")


def display_team_info(player: Player):
    """Display information about a player's team"""
    print(f"\n=== {player.name}'s Team ===")
    for i, pokemon in enumerate(player.team):
        status = "FAINTED" if pokemon.is_fainted else "OK"
        active_marker = " (ACTIVE)" if i == player.active_pokemon_index else ""
        print(f"{i + 1}. {pokemon.species.name} - {pokemon.current_hp}/{pokemon.max_hp} HP [{status}]{active_marker}")


def main():
    """Main function to run the Pokemon Battle Simulator"""
    print("=== Pokemon Battle Simulator ===")
    print("Welcome to the Pokemon Battle Simulator!")
    
    # Initialize the databases
    print("\nInitializing PokemonDex and MoveDex...")
    pokedex = PokemonDex()
    movedex = MoveDex()
    
    print(f"Loaded {len(pokedex.list_pokemon())} Pokemon species")
    print(f"Loaded {len(movedex.list_moves())} moves")
    
    # Display available Pokemon
    print(f"\nAvailable Pokemon: {', '.join(pokedex.list_pokemon())}")
    print(f"Available Moves: {', '.join(movedex.list_moves())}")
    
    # Create teams
    print("\n=== Team Setup ===")
    
    # Player 1
    print("\nPlayer 1, choose your team (up to 3 Pokemon):")
    team1_names = []
    available_pokemon = pokedex.list_pokemon()
    
    print("Available Pokemon:")
    for i, name in enumerate(available_pokemon):
        print(f"{i + 1}. {name}")
    
    while len(team1_names) < 3:
        try:
            choice = input(f"Choose Pokemon {len(team1_names) + 1} (name or number): ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_pokemon):
                    pokemon_name = available_pokemon[index]
                else:
                    print("Invalid number!")
                    continue
            else:
                pokemon_name = choice.title()
            
            if pokemon_name in available_pokemon and pokemon_name not in team1_names:
                team1_names.append(pokemon_name)
                print(f"Added {pokemon_name} to Player 1's team!")
            elif pokemon_name in team1_names:
                print("You already have that Pokemon!")
            else:
                print("Pokemon not found!")
        except (ValueError, KeyboardInterrupt):
            print("Invalid input!")
    
    # Player 2
    print("\nPlayer 2, choose your team (up to 3 Pokemon):")
    team2_names = []
    
    while len(team2_names) < 3:
        try:
            choice = input(f"Choose Pokemon {len(team2_names) + 1} (name or number): ").strip()
            
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_pokemon):
                    pokemon_name = available_pokemon[index]
                else:
                    print("Invalid number!")
                    continue
            else:
                pokemon_name = choice.title()
            
            if pokemon_name in available_pokemon and pokemon_name not in team2_names:
                team2_names.append(pokemon_name)
                print(f"Added {pokemon_name} to Player 2's team!")
            elif pokemon_name in team2_names:
                print("You already have that Pokemon!")
            else:
                print("Pokemon not found!")
        except (ValueError, KeyboardInterrupt):
            print("Invalid input!")
    
    # Create teams
    team1 = create_sample_team(pokedex, movedex, team1_names)
    team2 = create_sample_team(pokedex, movedex, team2_names)
    
    # Create players
    player1 = Player("Player 1", team1)
    player2 = Player("Player 2", team2)
    
    # Display team information
    display_team_info(player1)
    for pokemon in player1.team:
        display_pokemon_info(pokemon)
    
    display_team_info(player2)
    for pokemon in player2.team:
        display_pokemon_info(pokemon)
    
    # Start the battle
    input("\nPress Enter to start the battle...")
    battle = BattleManager(player1, player2)
    battle.start_battle()
    
    # Display final results
    print(f"\nFinal battle statistics:")
    print(f"Battle lasted {battle.turn_count} turns")
    display_team_info(player1)
    display_team_info(player2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBattle interrupted! Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this issue!")
