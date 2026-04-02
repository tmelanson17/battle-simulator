from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from src.state.pokestate_defs import Player, Status, Type, get_effectiveness


@dataclass
class Hazard:
    name: str
    type: Type
    max_layers: int = 1
    # Flat fraction of max HP dealt per layer. A list means per-layer values (index = layers-1).
    damage_per_layer: Union[float, List[float]] = 0.0
    # Fraction of max HP scaled by type effectiveness before applying (e.g. Stealth Rock).
    type_scaled_damage: float = 0.0
    # Status inflicted indexed by layer count (index = layers-1). None means no status.
    status_by_layer: List[Optional[Status]] = field(default_factory=list)
    # Entering Pokemon whose type matches a cleanse_type absorbs / removes the hazard.
    cleanse_types: List[Type] = field(default_factory=list)
    # Entering Pokemon of an immune type receive no damage or status from this hazard.
    immune_types: List[Type] = field(default_factory=list)


HAZARD_DEFS: Dict[str, Hazard] = {
    "Stealth Rock": Hazard(
        name="Stealth Rock",
        type=Type.ROCK,
        max_layers=1,
        type_scaled_damage=0.125,
    ),
    "Spikes": Hazard(
        name="Spikes",
        type=Type.GROUND,
        max_layers=3,
        damage_per_layer=[0.125, 1 / 6, 0.25],
        immune_types=[Type.FLYING],
    ),
    "Toxic Spikes": Hazard(
        name="Toxic Spikes",
        type=Type.POISON,
        max_layers=2,
        status_by_layer=[Status.POISONED, Status.TOXIC],
        cleanse_types=[Type.POISON],
    ),
}


@dataclass
class FieldSide:
    hazards: Dict[str, int] = field(default_factory=dict)  # hazard_name -> current layers


@dataclass
class FieldState:
    player_1_side: FieldSide = field(default_factory=FieldSide)
    player_2_side: FieldSide = field(default_factory=FieldSide)
    weather: Optional[str] = None  # "sun", "rain", "sand", "hail", or None

    def get_side(self, player: Player) -> FieldSide:
        if player == Player.PLAYER_1:
            return self.player_1_side
        return self.player_2_side


# ---------------------------------------------------------------------------
# Hazard application
# ---------------------------------------------------------------------------

def apply_hazards_on_entry(player: Player, game_state) -> None:
    """
    Apply all active hazards on `player`'s side to the Pokemon that just switched in.
    Must be called after switch_pokemon() so the incoming mon is already active.
    Imports GameState lazily to avoid circular imports.
    """
    from src.actions.status_actions import ApplyStatusAction

    player_state = game_state.battle_state.get_player(player)
    incoming_mon = player_state.get_active_mon(0)
    side = game_state.field_state.get_side(player)

    to_remove = []
    for hazard_name, layers in list(side.hazards.items()):
        hazard_def = HAZARD_DEFS.get(hazard_name)
        if hazard_def is None:
            continue

        incoming_types = [t for t in (incoming_mon.type1, incoming_mon.type2) if t is not None]

        # Check immunity: if the incoming Pokemon has any immune type, skip entirely.
        if any(t in hazard_def.immune_types for t in incoming_types):
            continue

        # Check cleanse: if the incoming Pokemon has a cleanse type, absorb the hazard.
        if any(t in hazard_def.cleanse_types for t in incoming_types):
            to_remove.append(hazard_name)
            print(f"{incoming_mon.name} absorbed the {hazard_name}!")
            continue

        # Calculate flat damage from damage_per_layer.
        flat_fraction = 0.0
        if isinstance(hazard_def.damage_per_layer, list):
            idx = min(layers, len(hazard_def.damage_per_layer)) - 1
            flat_fraction = hazard_def.damage_per_layer[idx]
        else:
            flat_fraction = hazard_def.damage_per_layer * layers

        # Calculate type-scaled damage (e.g. Stealth Rock).
        type_fraction = 0.0
        if hazard_def.type_scaled_damage > 0:
            effectiveness = 1.0
            for t in incoming_types:
                effectiveness *= get_effectiveness(hazard_def.type, t)
            type_fraction = hazard_def.type_scaled_damage * effectiveness

        total_damage = int((flat_fraction + type_fraction) * incoming_mon.hp_max)
        if total_damage > 0:
            print(f"{incoming_mon.name} was hurt by {hazard_name}! (-{total_damage} HP)")
            incoming_mon.hp = max(incoming_mon.hp - total_damage, 0)

        # Apply status if defined for this layer count.
        if hazard_def.status_by_layer and not incoming_mon.fainted:
            status_idx = min(layers, len(hazard_def.status_by_layer)) - 1
            status = hazard_def.status_by_layer[status_idx]
            if status is not None and not incoming_mon.statused:
                ApplyStatusAction(player, 0, status).execute(game_state)

    for hazard_name in to_remove:
        del side.hazards[hazard_name]
