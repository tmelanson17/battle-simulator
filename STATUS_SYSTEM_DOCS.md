# Status Effect Listener System

This document explains how the new status effect listener system works, particularly for implementing paralysis with proper immobility mechanics.

## Overview

The status effect system uses the existing listener framework to implement status effects like paralysis. The key innovation is that **status effects are implemented as listeners** that can intercept and modify the event queue, rather than being checked only at action execution time.

## Key Components

### 1. Status Effect Listeners

#### `ParalysisSpeedListener`
- **Purpose**: Applies and removes the 75% speed reduction when a Pokemon becomes paralyzed/cured
- **Listens to**: `BattleState` events
- **Behavior**: 
  - When Pokemon becomes paralyzed: reduces base speed to 25% of original
  - When Pokemon is cured: restores original base speed

#### `ParalysisImmobilityListener`
- **Purpose**: Prevents paralyzed Pokemon from executing move actions (30% chance)
- **Listens to**: `BattleState` events
- **Behavior**: 
  - Scans the event queue for `MoveAction`s from the paralyzed Pokemon
  - 30% chance to remove those actions from the queue
  - Works on actions that were queued **before** paralysis was applied

### 2. Status Effect Manager

The `StatusEffectManager` class handles:
- Applying status effects and registering appropriate listeners
- Cleaning up listeners when status effects are cured
- Managing listener lifecycles for fainted Pokemon

## How It Works

### The Problem This Solves

In traditional implementations, status effects are checked at execution time:

```python
def execute_move(self, battle_state):
    if self.pokemon.status == Status.PARALYZED:
        if random.random() < 0.3:
            print("Can't move due to paralysis!")
            return
    # Execute move normally
```

**Problem**: This only works if you check status at execution time. If a Pokemon is paralyzed AFTER the action is queued, it can still execute the move.

### Our Solution

Our listener-based approach works differently:

1. **Actions are queued** (normal battle flow)
2. **Status effects are applied** (adds listeners to the system)
3. **Listeners check the queue** (can remove/modify existing actions)
4. **Actions execute** (only if not prevented by listeners)

This means paralysis can prevent actions that were queued before the paralysis was applied!

## Integration Example

### Minimal Integration

To add this to your existing battle manager, you only need:

```python
class StatusAwareBattleManager(BattleManager):
    def __init__(self):
        super().__init__()
        self.status_manager = StatusEffectManager(self.listener_manager)
    
    def apply_thunder_wave(self, user_player, target_player, target_idx, battle_state):
        # Apply paralysis with listeners
        self.status_manager.apply_paralysis(target_player, target_idx, battle_state)
```

Your existing battle loop doesn't need to change - it already calls `listener_manager.listen()` which now includes status effect checks.

## Sequence Diagram

```
Turn Start
    ↓
Player 1 queues "Thunderbolt" action
Player 2 queues "Water Gun" action
    ↓
Player 1's "Thunder Wave" executes
    ↓ (applies paralysis)
StatusEffectManager.apply_paralysis()
    ↓
ParalysisSpeedListener added to listener_manager
ParalysisImmobilityListener added to listener_manager
    ↓
listener_manager.listen(battle_state, action_queue)
    ↓
ParalysisSpeedListener: reduces Player 2's speed
ParalysisImmobilityListener: 30% chance to remove Player 2's "Water Gun" from queue
    ↓
Continue executing remaining actions in queue
```

## Benefits

1. **Timing Independence**: Actions can be prevented regardless of when status is applied
2. **Clean Separation**: Status effects are separate from action execution logic
3. **Extensible**: Easy to add new status effects following the same pattern
4. **Automatic Cleanup**: Listeners are automatically managed and cleaned up
5. **Minimal Integration**: Works with existing battle manager with minimal changes

## Extending the System

To add new status effects (like Sleep, Poison, etc.), follow this pattern:

1. Create a new listener class that extends `Listener[BattleState]`
2. Implement the status effect logic in the `on_event` method
3. Add it to the `StatusEffectManager.apply_*` methods
4. Handle cleanup in `cure_status` and `cleanup_fainted_pokemon`

## Example: Adding Sleep

```python
class SleepImmobilityListener(Listener[BattleState]):
    datatype = BattleState
    
    def __init__(self, player: Player, pokemon_idx: int):
        self.player = player
        self.pokemon_idx = pokemon_idx
    
    def on_event(self, input: BattleState, event_queue: EventQueue):
        pokemon = input.get_player(self.player).pk_list[self.pokemon_idx]
        
        if pokemon.status == Status.SLEEP:
            # Remove ALL move actions (100% immobilization)
            event_queue.remove_event(lambda event: 
                isinstance(event, MoveAction) and 
                event.player == self.player and 
                event.src_idx == self.pokemon_idx
            )
            print(f"{pokemon.name} is fast asleep!")
```

## Testing

The system includes comprehensive tests in `test_paralysis_listeners.py` that demonstrate:

- Actions queued before paralysis can still be prevented
- Speed reduction works correctly
- Status curing removes listeners properly
- Random chance mechanics work as expected

Run the tests with:
```bash
python test_paralysis_listeners.py
```

## Files

- `src/events/status_listeners.py` - Core listener implementations
- `test_paralysis_listeners.py` - Comprehensive test suite
- `integration_demo.py` - Simple integration example
- `status_example.py` - Basic usage example
