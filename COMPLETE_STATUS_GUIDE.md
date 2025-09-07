# Complete Status Effect System Guide

This guide covers all implemented status effects and how to use them in your Pokemon battle simulator.

## Implemented Status Effects

### 1. **Paralysis** (`Status.PARALYZED`)
- **Speed Effect**: Reduces speed by 75% (to 25% of original)
- **Movement**: 30% chance to be unable to move each turn
- **Applied by**: Thunder Wave, Stun Spore

```python
# Apply paralysis
status_manager.apply_paralysis(Player.PLAYER_2, 0, battle_state)

# Effects:
# - Pokemon's speed immediately reduced
# - 30% chance for move actions to be removed from queue
```

### 2. **Poison** (`Status.POISONED`)
- **Damage**: 12.5% of max HP each turn
- **Applied by**: Poison Powder, Poison Sting

```python
# Apply poison
status_manager.apply_poison(Player.PLAYER_2, 0, battle_state)

# Effects:
# - Fixed damage each turn
# - Pokemon can faint from poison damage
```

### 3. **Toxic** (`Status.TOXIC`)
- **Damage**: Increasing damage each turn (6.25% × turn number)
- **Turn 1**: 6.25% damage
- **Turn 2**: 12.5% damage  
- **Turn 3**: 18.75% damage
- **Turn 4**: 25% damage, etc.

```python
# Apply toxic
status_manager.apply_toxic(Player.PLAYER_2, 0, battle_state)

# Effects:
# - Escalating damage that becomes very dangerous
# - Resets counter when Pokemon switches out
```

### 4. **Burn** (`Status.BURNED`)
- **Attack Effect**: Reduces physical attack by 50%
- **Damage**: 12.5% of max HP each turn
- **Applied by**: Ember, Fire Blast, Will-O-Wisp

```python
# Apply burn
status_manager.apply_burn(Player.PLAYER_2, 0, battle_state)

# Effects:
# - Immediate attack reduction
# - Damage each turn
# - Physical moves deal half damage
```

### 5. **Sleep** (`Status.SLEEP`)
- **Movement**: Pokemon cannot move for 1-3 turns
- **Duration**: Randomly determined when applied
- **Applied by**: Sleep Powder, Hypnosis

```python
# Apply sleep
status_manager.apply_sleep(Player.PLAYER_2, 0, battle_state)

# Effects:
# - All move actions removed from queue while asleep
# - Automatically wakes up after 1-3 turns
```

### 6. **Freeze** (`Status.FROZEN`)
- **Movement**: Pokemon cannot move
- **Thaw Chance**: 20% chance to thaw each turn
- **Thaw on Fire**: Hit by Fire-type move will thaw (not fully implemented)
- **Applied by**: Ice moves, Blizzard

```python
# Apply freeze
status_manager.apply_freeze(Player.PLAYER_2, 0, battle_state)

# Effects:
# - All move actions removed from queue while frozen
# - 20% chance to thaw each turn
```

## Integration with Your Battle Manager

### Simple Integration

```python
from src.events.status_listeners import StatusEffectManager

class YourBattleManager(BattleManager):
    def __init__(self):
        super().__init__()
        # Add status effect manager
        self.status_manager = StatusEffectManager(self.listener_manager)
    
    # Your existing execution_loop already works!
    # The listener_manager.listen() call handles everything
```

### Applying Status Effects

You can apply status effects from moves:

```python
# In your move execution logic
def execute_thunder_wave(self, user_player, target_player, target_idx, battle_state):
    success = self.status_manager.apply_paralysis(target_player, target_idx, battle_state)
    if not success:
        print("Thunder Wave had no effect!")
```

### Status Effect Actions

Use `ApplyStatusAction` for move effects:

```python
from src.events.status_listeners import ApplyStatusAction

# Create a status application action
apply_paralysis = ApplyStatusAction(
    user_player,           # Player using the move
    target_player,         # Target player
    target_idx,           # Target Pokemon index
    Status.PARALYZED,     # Status to apply
    self.status_manager   # Status manager
)

# Add to event queue
event_queue.add_event(apply_paralysis, priority)
```

## Status Effect Mechanics

### Status Protection
- Pokemon can only have **one status condition** at a time
- Attempting to apply a status to an already statused Pokemon will fail
- Fainted status doesn't prevent other status applications

### Listener Management
- Listeners are automatically added when status is applied
- Listeners are automatically removed when status is cured
- Listeners are cleaned up when Pokemon faint

### Turn Order Effects
- **Speed changes** (paralysis, etc.) affect turn order immediately
- **Damage effects** occur at the end of each turn
- **Immobility effects** can prevent already-queued actions

## Advanced Usage

### Manual Status Curing

```python
# Cure a specific status
pokemon.status = Status.NONE
status_manager.cure_status(player, pokemon_idx, Status.PARALYZED)

# Clean up when Pokemon faints
status_manager.cleanup_fainted_pokemon(player, pokemon_idx)
```

### Custom Status Moves

```python
def create_status_move_action(move_name, user_player, target_idx, status_manager):
    """Create status move actions for common moves"""
    
    if move_name == "Thunder Wave":
        return StatusAwareMoveAction(user_player, 2, 0, target_idx, status_manager)
    elif move_name == "Sleep Powder":
        # Would apply Sleep status
        return StatusAwareMoveAction(user_player, 2, 0, target_idx, status_manager)
    # Add more moves as needed
```

### End-of-Turn Processing

Your battle loop should trigger listeners for end-of-turn effects:

```python
# In your turn processing
def end_turn(self, battle_state):
    # Trigger end-of-turn effects (poison damage, burn damage, etc.)
    self.listener_manager.listen(battle_state, self._action_queue)
    
    # Check for fainted Pokemon
    self.check_for_fainted_pokemon(battle_state)
```

## Example Battle Flow

```python
# Turn 1: Pikachu uses Thunder Wave on Squirtle
thunder_wave = StatusAwareMoveAction(Player.PLAYER_1, 2, 0, 0, status_manager)
action_queue.add_event(thunder_wave, priority)

# Turn 2: Squirtle tries to use Water Gun (might be prevented by paralysis)
water_gun = MoveAction(Player.PLAYER_2, 0, 0, 0)
action_queue.add_event(water_gun, priority)

# Execute actions
while not action_queue.empty():
    priority, action = action_queue.get_next_event()
    action.execute(battle_state, action_queue)
    
    # This call handles status effects!
    listener_manager.listen(battle_state, action_queue)
```

## Testing Your Status Effects

Run the comprehensive test:

```bash
python test_all_status_effects.py
```

This test demonstrates:
- All status effects working correctly
- Proper damage calculations
- Immobility mechanics
- Status protection
- Listener cleanup

## Performance Notes

- Status listeners are only active when Pokemon have the corresponding status
- Listeners are automatically cleaned up to prevent memory leaks  
- The system scales well with multiple Pokemon having different status effects
- Queue scanning is efficient even with many actions

## Future Extensions

The system is designed to be easily extensible. To add new status effects:

1. Create a new listener class
2. Add the status to the `Status` enum
3. Add an `apply_*` method to `StatusEffectManager`
4. Update `ApplyStatusAction` to handle the new status

The listener framework handles all the complexity of timing, cleanup, and integration automatically.
