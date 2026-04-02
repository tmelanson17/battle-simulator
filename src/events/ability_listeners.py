from src.events.listener import Listener
from src.events.event_queue import EventQueue
from src.state.pokestate_defs import MoveHitEvent, Player, Type


class VoltAbsorbListener(Listener[MoveHitEvent]):
    """
    Absorbs Electric-type moves targeting this Pokemon and restores 25% max HP.
    Stays registered for the lifetime of the Pokemon in play.
    """
    datatype = MoveHitEvent

    def __init__(self, player: Player, slot: int, game_state):
        self.player = player
        self.slot = slot
        self._game_state = game_state

    def on_event(self, event: MoveHitEvent, event_queue: EventQueue) -> bool:
        if event.attacker == self.player:
            return True  # We're the attacker, not the target
        if event.move.type != Type.ELECTRIC:
            return True
        my_mon = (
            self._game_state.battle_state
            .get_player(self.player)
            .get_active_mon(self.slot)
        )
        if event.target_mon is not my_mon:
            return True

        event.absorbed = True
        heal_amount = int(my_mon.hp_max * 0.25)
        from src.actions.actions import HealAction
        from src.events.priority import Priority
        event_queue.add_event(
            HealAction(self.player, heal_amount, self.slot),
            Priority(0, 0),
        )
        print(f"{my_mon.name}'s Volt Absorb absorbed the Electric move!")
        return True  # Stay registered


class LevitateListener(Listener[MoveHitEvent]):
    """
    Gives immunity to Ground-type moves.
    Stays registered for the lifetime of the Pokemon in play.
    """
    datatype = MoveHitEvent

    def __init__(self, player: Player, slot: int, game_state):
        self.player = player
        self.slot = slot
        self._game_state = game_state

    def on_event(self, event: MoveHitEvent, event_queue: EventQueue) -> bool:
        if event.attacker == self.player:
            return True  # We're the attacker, not the target
        if event.move.type != Type.GROUND:
            return True
        my_mon = (
            self._game_state.battle_state
            .get_player(self.player)
            .get_active_mon(self.slot)
        )
        if event.target_mon is not my_mon:
            return True

        event.absorbed = True
        print(f"{my_mon.name} is floating — it's unaffected by Ground moves!")
        return True  # Stay registered


class FlashFireListener(Listener[MoveHitEvent]):
    """
    Absorbs Fire-type moves (defensive). Once activated, boosts the power of
    the user's own Fire-type moves by 1.5x (offensive).
    Stays registered for the lifetime of the Pokemon in play.
    """
    datatype = MoveHitEvent

    def __init__(self, player: Player, slot: int, game_state):
        self.player = player
        self.slot = slot
        self._game_state = game_state
        self.flash_fire_active = False

    def on_event(self, event: MoveHitEvent, event_queue: EventQueue) -> bool:
        my_mon = (
            self._game_state.battle_state
            .get_player(self.player)
            .get_active_mon(self.slot)
        )
        if event.move.type != Type.FIRE:
            return True

        if event.attacker != self.player:
            # Defensive: we're being hit by a Fire move
            if event.target_mon is not my_mon:
                return True
            event.absorbed = True
            if not self.flash_fire_active:
                self.flash_fire_active = True
                print(f"{my_mon.name}'s Flash Fire absorbed the Fire move and powered up!")
            else:
                print(f"{my_mon.name}'s Flash Fire absorbed the Fire move!")
        else:
            # Offensive: we're using a Fire move while Flash Fire is active
            if event.src_mon is not my_mon:
                return True
            if self.flash_fire_active:
                event.damage_multiplier *= 1.5
                print(f"{my_mon.name}'s Flash Fire boosted the move's power!")

        return True  # Stay registered
