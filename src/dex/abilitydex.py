from typing import Dict, Optional

from src.state.pokestate_defs import Ability

ABILITY_DEX: Dict[str, Ability] = {
    "intimidate": Ability(
        name="Intimidate",
        description="Lowers the opposing Pokemon's Attack by one stage upon switching in.",
    ),
    "drought": Ability(
        name="Drought",
        description="Summons harsh sunlight when the Pokemon enters the battle.",
    ),
    "voltabsorb": Ability(
        name="Volt Absorb",
        description="Absorbs Electric-type moves, restoring 25% of max HP instead of taking damage.",
    ),
    "flashfire": Ability(
        name="Flash Fire",
        description="Absorbs Fire-type moves and boosts the power of the user's Fire-type moves by 1.5x.",
    ),
    "levitate": Ability(
        name="Levitate",
        description="Gives immunity to Ground-type moves.",
    ),
}


def _normalize(name: str) -> str:
    return name.replace(" ", "").replace("-", "").lower()


def get_ability_by_name(name: str) -> Optional[Ability]:
    return ABILITY_DEX.get(_normalize(name))
