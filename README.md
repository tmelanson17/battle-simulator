# Pokemon Battle Simulator

A Python application that simulates Pokemon battles with a comprehensive MoveDex, PokemonDex, and BattleManager system.

## Features

### MoveDex
- Database of Pokemon moves with complete descriptions
- Each move includes:
  - Type (Fire, Water, Electric, etc.)
  - Category (Physical, Special, Status)
  - Power, Accuracy, PP (Power Points)
  - Priority level
  - Primary and secondary effects

### PokemonDex
- Database of Pokemon species with detailed information
- Each Pokemon includes:
  - Unique index number
  - Type(s) (single or dual-type)
  - Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)

### BattleManager
- Turn-based battle system between two players
- Features:
  - Priority-based move execution (move priority + Pokemon speed)
  - Type effectiveness calculations
  - Damage calculation with STAB (Same Type Attack Bonus)
  - Status move support
  - Pokemon switching when fainted
  - Win condition detection

## Project Structure

```
battle-simulator/
├── main.py              # Main application entry point
├── movedex.py           # Move database and Move class
├── pokemondex.py        # Pokemon database and PokemonSpecies class
├── pokemon.py           # Individual Pokemon instance class
├── player.py            # Player class for battle participants
├── battle_manager.py    # Battle management and execution
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone or download this repository
3. Navigate to the project directory
4. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:

```bash
python main.py
```

### How to Play

1. **Team Selection**: Each player chooses up to 3 Pokemon from the available roster
2. **Battle Start**: The battle begins with each player's first Pokemon
3. **Turn System**: Each turn, players select moves for their active Pokemon
4. **Move Execution**: Moves are executed based on priority and speed
5. **Pokemon Management**: When a Pokemon faints, the player must choose a replacement
6. **Victory**: The first player to defeat all of the opponent's Pokemon wins

### Available Pokemon (Starter Set)

- Bulbasaur (Grass/Poison)
- Charmander (Fire)
- Squirtle (Water)
- Pikachu (Electric)
- Jigglypuff (Normal/Fairy)
- Psyduck (Water)
- Cubone (Ground)
- Eevee (Normal)

### Available Moves (Starter Set)

- **Tackle** (Normal/Physical): Basic damage move
- **Quick Attack** (Normal/Physical): High priority move
- **Thunderbolt** (Electric/Special): Strong electric attack with paralysis chance
- **Water Gun** (Water/Special): Basic water attack
- **Ember** (Fire/Special): Basic fire attack with burn chance
- **Vine Whip** (Grass/Physical): Basic grass attack
- **Thunder Wave** (Electric/Status): Paralyzes the target
- **Agility** (Psychic/Status): Increases Speed stat

## Game Mechanics

### Damage Calculation
- Based on attack/defense stats, move power, and type effectiveness
- Includes STAB (Same Type Attack Bonus) when move type matches Pokemon type
- Random factor applied (85-100% of calculated damage)

### Type Effectiveness
- Super effective moves deal 2x damage
- Not very effective moves deal 0.5x damage
- No effect moves deal 0x damage
- Partial type chart implemented (can be expanded)

### Stat Calculations
- Stats calculated using simplified Pokemon formula
- Base stats modified by level (default level 50)
- Stat stages can be modified by status moves (-6 to +6)

## Extending the Game

### Adding New Pokemon
```python
from pokemondex import PokemonSpecies, BaseStats, PokemonType

new_pokemon = PokemonSpecies(
    index=150,
    name="Mewtwo",
    type1=PokemonType.PSYCHIC,
    base_stats=BaseStats(106, 110, 90, 154, 90, 130)
)

pokedex.add_pokemon(new_pokemon)
```

### Adding New Moves
```python
from movedex import Move, MoveType, MoveCategory

new_move = Move(
    name="Psychic",
    move_type=MoveType.PSYCHIC,
    category=MoveCategory.SPECIAL,
    power=90,
    accuracy=100,
    pp=10,
    priority=0,
    primary_effect="Deals damage",
    secondary_effect="10% chance to lower Sp. Defense"
)

movedex.add_move(new_move)
```

## Future Enhancements

- [ ] Complete type effectiveness chart
- [ ] Status conditions (paralysis, burn, sleep, etc.)
- [ ] Pokemon abilities
- [ ] Items and held items
- [ ] Critical hit calculations
- [ ] More sophisticated AI players
- [ ] Battle replay system
- [ ] Save/load functionality
- [ ] GUI interface

## Contributing

This is a educational project demonstrating object-oriented programming concepts in Python. Feel free to extend and modify the code for learning purposes.

## License

This project is for educational purposes only. Pokemon is a trademark of Nintendo/Game Freak.
