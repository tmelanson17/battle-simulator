#!/usr/bin/env python3
"""
Pokemon Battle Simulator
A Python application that simulates Pokemon battles with MoveDex, PokemonDex, and BattleManager.
"""

import sys
import src.dex.gen1_dex as gen1_dex
from src.state.pokestate import (
    create_default_battle_state,
    create_battle_state_from_team_files,
)
from battle_manager_rewrite import BattleManager


DEFAULT_MOVES = {
    "Pikachu": ["Thunderbolt", "Quick Attack", "Thunder Wave", "Seismic Toss"],
    "Bulbasaur": ["Vine Whip", "Tackle", "Growth", "Sleep Powder"],
    "Ivysaur": ["Vine Whip", "Tackle", "Growth", "Sleep Powder"],
    "Venusaur": ["Vine Whip", "Tackle", "Growth", "Sleep Powder"],
    "Charmander": ["Ember", "Scratch", "Growl", "Leer"],
    "Charmeleon": ["Ember", "Scratch", "Growl", "Leer"],
    "Charizard": ["Ember", "Scratch", "Growl", "Leer"],
    "Squirtle": ["Water Gun", "Tackle", "Bubble", "Withdraw"],
    "Wartortle": ["Water Gun", "Tackle", "Bubble", "Withdraw"],
    "Blastoise": ["Water Gun", "Tackle", "Bubble", "Withdraw"],
    "Pidgey": ["Quick Attack", "Gust", "Sand Attack"],
    "Rattata": ["Quick Attack", "Tackle", "Tail Whip"],
    "Gengar": ["Night Shade", "Giga Drain", "Hypnosis", "Psychic"],
}
DEFAULT_MOVESET = ["Tackle", "Quick Attack"]


def get_default_moves(name: str) -> list:
    return DEFAULT_MOVES.get(name, DEFAULT_MOVESET)


def select_team(player_name: str, available_pokemon: list) -> list:
    print(f"\n{player_name}, choose your team (up to 3 Pokemon):")
    print("Available Pokemon:")
    for i, name in enumerate(available_pokemon):
        print(f"  {i + 1}. {name}")

    team = []
    while len(team) < 3:
        try:
            choice = input(f"Choose Pokemon {len(team) + 1} (name or number): ").strip()

            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_pokemon):
                    pokemon_name = available_pokemon[index]
                else:
                    print("Invalid number!")
                    continue
            else:
                pokemon_name = choice.title()

            if pokemon_name in available_pokemon and pokemon_name not in team:
                team.append(pokemon_name)
                print(f"Added {pokemon_name} to {player_name}'s team!")
            elif pokemon_name in team:
                print("You already have that Pokemon!")
            else:
                print("Pokemon not found!")
        except (ValueError, KeyboardInterrupt):
            print("Invalid input!")

    return team


def main():
    print("=== Pokemon Battle Simulator ===")
    print("Welcome to the Pokemon Battle Simulator!")

    if len(sys.argv) == 3:
        team1_file, team2_file = sys.argv[1], sys.argv[2]
        print(f"\nLoading teams from files: {team1_file}, {team2_file}")
        battle_state = create_battle_state_from_team_files(team1_file, team2_file)
    else:
        available_pokemon = [info.species for info in gen1_dex.GEN1_POKEMON.values()]

        team1_names = select_team("Player 1", available_pokemon)
        team2_names = select_team("Player 2", available_pokemon)

        moves1 = [get_default_moves(name) for name in team1_names]
        moves2 = [get_default_moves(name) for name in team2_names]

        print(f"\nPlayer 1's team: {', '.join(team1_names)}")
        print(f"Player 2's team: {', '.join(team2_names)}")

        battle_state = create_default_battle_state(
            team1_names, team2_names, moves1, moves2
        )

    input("\nPress Enter to start the battle...")

    battle_manager = BattleManager(battle_state)
    battle_manager.execution_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBattle interrupted! Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this issue!")
