from src.events.listener import Listener
from src.events.event_queue import EventQueue
from src.state.pokestate_defs import Player, Status, SwitchInEvent, get_effectiveness, calculate_damage


class PursuitListener(Listener[SwitchInEvent]):
    """
    Registered by ChooseAction as soon as the player selects Pursuit — before any
    events execute for the turn.  This guarantees the listener is in place even
    when SwitchIn fires first (priority bracket 6 > Pursuit's bracket 0).

    If the opponent switches out on the same turn:
      - Damage is calculated and applied to the switching-out Pokemon *before*
        switch_pokemon() runs.
      - The pending MoveAction for Pursuit is removed from the queue so it does
        not fire again at the end of the turn.

    If no switch occurs the listener is never triggered and the MoveAction fires
    normally, queuing a DamageAction at its standard priority.
    """

    datatype = SwitchInEvent

    def __init__(self, pursuing_player: Player, game_state,
                 move_idx: int, src_idx: int, target_idx: int):
        self.pursuing_player = pursuing_player
        self._game_state = game_state  # lightweight reference, not a copy
        self.move_idx = move_idx
        self.src_idx = src_idx
        self.target_idx = target_idx

    def on_event(self, event: SwitchInEvent, event_queue: EventQueue) -> bool:
        # Only intercept when the *opponent* is the one switching.
        if event.player != Player.opponent(self.pursuing_player):
            return True  # keep listening

        from src.dex.moves import get_move_by_name
        from src.actions.move_action import MoveAction

        src_mon = (
            self._game_state.battle_state
            .get_player(self.pursuing_player)
            .get_active_mon(self.src_idx)
        )

        # Status conditions that always prevent acting.
        if src_mon.status in (Status.SLEEP, Status.FROZEN, Status.FAINTED):
            print(f"{src_mon.name} can't move due to {src_mon.status}!")
            event_queue.remove_event(
                lambda e: (
                    isinstance(e, MoveAction)
                    and e.player == self.pursuing_player
                    and e.move_idx == self.move_idx
                    and e.src_idx == self.src_idx
                )
            )
            return False

        # A status effect (e.g. paralysis) may have already removed the MoveAction
        # from the queue before SwitchIn fired.  If so, the user can't act.
        move_still_queued = any(
            isinstance(queued.event, MoveAction)
            and queued.event.player == self.pursuing_player
            and queued.event.move_idx == self.move_idx
            and queued.event.src_idx == self.src_idx
            for queued in event_queue.get_all_events()
        )
        if not move_still_queued:
            return False

        target_mon = (
            self._game_state.battle_state
            .get_player(event.player)
            .get_active_mon(event.slot)
        )
        dex_entry = get_move_by_name("Pursuit")

        effectiveness = 1.0
        if target_mon.type1:
            effectiveness *= get_effectiveness(dex_entry.type, target_mon.type1)
        if target_mon.type2:
            effectiveness *= get_effectiveness(dex_entry.type, target_mon.type2)

        if effectiveness == 0:
            print(f"Pursuit had no effect on {target_mon.name}!")
        else:
            stab = (
                1.5 if (dex_entry.type == src_mon.type1 or dex_entry.type == src_mon.type2)
                else 1.0
            )
            damage = calculate_damage(
                dex_entry.power,
                src_mon.get_offensive_stat(dex_entry.category),
                target_mon.get_defensive_stat(dex_entry.category),
                effectiveness,
                stab,
            )
            if damage > 0 and not target_mon.fainted:
                target_mon.hp = max(target_mon.hp - damage, 0)
                print(f"Pursuit dealt {damage} damage to {target_mon.name} as it fled!")

        # Remove the pending MoveAction for Pursuit so it does not fire at end-of-turn.
        event_queue.remove_event(
            lambda e: (
                isinstance(e, MoveAction)
                and e.player == self.pursuing_player
                and e.move_idx == self.move_idx
                and e.src_idx == self.src_idx
            )
        )

        return False  # remove this listener; Pursuit has now resolved
