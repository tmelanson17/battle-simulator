from src.actions.actions import Action
from src.events.game_state import GameState
from src.state.pokestate_defs import Player
from src.events.priority import Priority


def _normalize(name: str) -> str:
    return name.replace(" ", "").replace("-", "").lower()


class AbilityRegisterAction(Action):
    """
    Queued by SwitchIn after entry hazards resolve (priority 5).
    Looks up the incoming Pokemon's ability and either applies an immediate
    effect (Intimidate, Drought) or registers a passive listener (Volt Absorb,
    Flash Fire, Levitate).
    """

    def __init__(self, player: Player, slot: int = 0):
        super().__init__(player)
        self.slot = slot

    def execute(self, game_state: GameState):
        from src.dex.abilitydex import get_ability_by_name

        mon = game_state.battle_state.get_player(self.player).get_active_mon(self.slot)
        if mon is None or mon.fainted or mon.ability is None:
            return

        ability = get_ability_by_name(mon.ability)
        if ability is None:
            return

        print(f"{mon.name}'s ability: {ability.name}!")
        normalized = _normalize(mon.ability)

        if normalized == "intimidate":
            self._apply_intimidate(game_state, mon)
        elif normalized == "drought":
            self._apply_drought(game_state, mon)
        elif normalized == "voltabsorb":
            self._register_volt_absorb(game_state)
        elif normalized == "flashfire":
            self._register_flash_fire(game_state)
        elif normalized == "levitate":
            self._register_levitate(game_state)

    def _apply_intimidate(self, game_state: GameState, mon) -> None:
        from src.actions.actions import EffectAction
        from src.actions.effects import PokemonEffect

        opponent = Player.opponent(self.player)
        opp_mon = game_state.battle_state.get_player(opponent).get_active_mon(0)
        print(f"{mon.name}'s Intimidate lowered {opp_mon.name}'s Attack!")
        game_state.event_queue.add_event(
            EffectAction(opponent, PokemonEffect("attack", "-1"), 0),
            Priority(4, 0),
        )

    def _apply_drought(self, game_state: GameState, mon) -> None:
        game_state.field_state.weather = "sun"
        print(f"The sunlight turned harsh due to {mon.name}'s Drought!")

    def _register_volt_absorb(self, game_state: GameState) -> None:
        from src.events.ability_listeners import VoltAbsorbListener

        game_state.listener_manager.add_listener(
            (self.player, self.slot),
            VoltAbsorbListener(self.player, self.slot, game_state),
        )

    def _register_flash_fire(self, game_state: GameState) -> None:
        from src.events.ability_listeners import FlashFireListener

        game_state.listener_manager.add_listener(
            (self.player, self.slot),
            FlashFireListener(self.player, self.slot, game_state),
        )

    def _register_levitate(self, game_state: GameState) -> None:
        from src.events.ability_listeners import LevitateListener

        game_state.listener_manager.add_listener(
            (self.player, self.slot),
            LevitateListener(self.player, self.slot, game_state),
        )
