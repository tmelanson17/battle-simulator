from src.actions.actions import Action, DamageAction
from src.actions.status_actions import ApplyStatusAction
from src.state.pokestate import Player, BattleState, PokemonState
from src.state.pokestate_defs import (
    Player,
    Move,
    Status,
    Category,
    Target,
    get_effectiveness,
    calculate_damage,
)
from src.state.field import HAZARD_DEFS
from src.events.game_state import GameState
from src.dex.moves import get_move_by_name
from src.actions.effects import from_move
from src.events.priority import Priority


class MoveAction(Action):
    def __init__(self, player: Player, move_idx: int, src_idx, target_idx):
        super().__init__(player)
        self.player = player
        self.move_idx = move_idx
        self.src_idx = src_idx
        self.target_idx = target_idx

    def calculate_move_damage(
        self, move: Move, src_mon: PokemonState, target_mon: PokemonState
    ) -> int:
        if move.fixed_damage is not None:
            effectiveness = 1.0
            if target_mon.type1:
                effectiveness *= get_effectiveness(move.type, target_mon.type1)
            if target_mon.type2:
                effectiveness *= get_effectiveness(move.type, target_mon.type2)
            if effectiveness == 0:
                return 0
            if move.fixed_damage == "level":
                return src_mon.level
            return 0

        base_power = move.power
        if base_power is None:
            return 0
        effectiveness = 1.0
        if target_mon.type1:
            effectiveness *= get_effectiveness(move.type, target_mon.type1)
        if target_mon.type2:
            effectiveness *= get_effectiveness(move.type, target_mon.type2)
        if effectiveness < 1.0:
            print("It's not very effective...")
        elif effectiveness > 1.0:
            print("It's super effective!")
        if effectiveness == 0:
            return 0
        stab_multiplier = 1.0
        if move.type == src_mon.type1 or move.type == src_mon.type2:
            stab_multiplier = 1.5
        offensive_stat = src_mon.get_offensive_stat(move.category)
        defensive_stat = target_mon.get_defensive_stat(move.category)
        return calculate_damage(
            base_power, offensive_stat, defensive_stat, effectiveness, stab_multiplier
        )

    def execute(self, game_state: GameState):
        player = game_state.battle_state.get_player(self.player)
        src_mon = player.get_active_mon(self.src_idx)
        move = src_mon.moves[self.move_idx]
        dex_entry = get_move_by_name(move.name)
        if move.disabled:
            return
        if not dex_entry:
            raise ValueError(f"Move {move.name} not found in dex....")
        if dex_entry.target == Target.SELF:
            target = src_mon
        else:
            target = game_state.battle_state.get_opponent(self.player).get_active_mon(
                self.target_idx
            )
        target_str = "" if dex_entry.target == Target.SELF else f" on {target.name}"
        print(f"{src_mon.name} used {dex_entry.name}{target_str}!")

        if dex_entry.category != Category.STATUS:
            # TODO: Handle damage / healing to self target moves
            if dex_entry.target == Target.SELF:
                raise NotImplementedError(
                    "Currently only opponent targeting moves are implemented."
                )
            damage = self.calculate_move_damage(dex_entry, src_mon, target)
            if damage > 0:
                game_state.event_queue.add_event(
                    DamageAction(self.player, damage, self.src_idx, self.target_idx),
                    Priority(dex_entry.priority, src_mon.speed),
                )
                if dex_entry.name == "Pursuit":
                    # Pursuit fired normally (opponent didn't switch) — clean up the
                    # PursuitListener so it doesn't fire on a future opponent switch.
                    from src.state.pokestate_defs import SwitchInEvent
                    from src.events.pursuit_listener import PursuitListener
                    game_state.listener_manager.remove_listener_if(
                        SwitchInEvent,
                        lambda lst: (
                            isinstance(lst, PursuitListener)
                            and lst.pursuing_player == self.player
                            and lst.src_idx == self.src_idx
                        ),
                    )
            else:
                print(f"It had no effect on {target.name}.")
        else:
            for effect in from_move(dex_entry):
                if effect.property.name == "status":
                    print(f"Applying status effect {effect.value}...")
                    # Currently only support inflicting status on target
                    game_state.event_queue.add_event(
                        ApplyStatusAction(
                            Player.opponent(self.player),
                            self.target_idx,
                            Status(effect.value.lower()),
                        ),
                        Priority(dex_entry.priority, src_mon.speed),
                    )
                else:
                    # TODO: Separate stat boosting effects from other effects
                    boost_name = (
                        "boosted" if effect.value.startswith("+") else "lowered"
                    )
                    if dex_entry.target == Target.SELF:
                        print(
                            f"{src_mon.name} {boost_name} its {effect.property.name} by {int(effect.value)}!"
                        )
                    else:
                        print(
                            f"{src_mon.name} {boost_name} {target.name}'s {effect.property.name} by {effect.value}!"
                        )
                    effect.apply(target)

        # Hazard setting: place a hazard layer on the opponent's side.
        if dex_entry.hazard_set:
            opponent_side = game_state.field_state.get_side(Player.opponent(self.player))
            hazard_def = HAZARD_DEFS.get(dex_entry.hazard_set)
            if hazard_def:
                current = opponent_side.hazards.get(dex_entry.hazard_set, 0)
                if current < hazard_def.max_layers:
                    opponent_side.hazards[dex_entry.hazard_set] = current + 1
                    print(f"{dex_entry.hazard_set} was set on the opposing side! (layer {current + 1})")
                else:
                    print(f"{dex_entry.hazard_set} is already at maximum layers!")

        # Hazard removal: clear all hazards from the user's own side.
        if dex_entry.hazard_remove:
            my_side = game_state.field_state.get_side(self.player)
            if my_side.hazards:
                removed = list(my_side.hazards.keys())
                my_side.hazards.clear()
                print(f"{src_mon.name} cleared {', '.join(removed)} from the field!")
