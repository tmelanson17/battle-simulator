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
        move = player.get_active_mon(self.src_idx).moves[self.move_idx]
        dex_entry = get_move_by_name(move.name)
        if move.disabled:
            return
        if dex_entry.target == Target.SELF:
            target = player.get_active_mon(self.src_idx)
        else:
            target = game_state.battle_state.get_opponent(self.player).get_active_mon(
                self.target_idx
            )
        target_str = "" if dex_entry.target == Target.SELF else f" on {target.name}"
        print(
            f"{player.get_active_mon(self.src_idx).name} used {dex_entry.name}{target_str}!"
        )
        if not dex_entry:
            raise ValueError(f"Move {move.name} not found in dex....")

        if dex_entry.category != Category.STATUS:
            # TODO: Handle damage / healing to self target moves
            if dex_entry.target == Target.SELF:
                raise NotImplementedError(
                    "Currently only opponent targeting moves are implemented."
                )
            damage = self.calculate_move_damage(
                dex_entry, player.get_active_mon(self.src_idx), target
            )
            if damage > 0:
                game_state.event_queue.add_event(
                    DamageAction(self.player, damage, self.src_idx, self.target_idx),
                    Priority(
                        dex_entry.priority, player.get_active_mon(self.src_idx).speed
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
                        Priority(
                            dex_entry.priority,
                            player.get_active_mon(self.src_idx).speed,
                        ),
                    )
                else:
                    # TODO: Separate stat boosting effects from other effects
                    boost_name = (
                        "boosted" if effect.value.startswith("+") else "lowered"
                    )
                    if dex_entry.target == Target.SELF:
                        print(
                            f"{player.get_active_mon(self.src_idx).name} {boost_name} its {effect.property.name} by {int(effect.value)}!"
                        )
                    else:
                        print(
                            f"{player.get_active_mon(self.src_idx).name} {boost_name} {target.name}'s {effect.property.name} by {effect.value}!"
                        )
                    effect.apply(target)
