from typing import List, Optional

from src.dex.gen1_moves import GEN1_MOVES, Move

ALL_MOVES = GEN1_MOVES

def normalize_move_name(name: str) -> str:
    """Transform a move name by removing spaces and converting to lowercase."""
    return name.replace(" ", "").replace("-", "").lower()

def get_move_by_name(name: str) -> Optional[Move]:
    """Get a specific move by name (handles both spaced and non-spaced names)."""
    normalized_search = normalize_move_name(name)
    for move in ALL_MOVES:
        if normalize_move_name(move.name) == normalized_search:
            return move
    return None

def get_move_name_by_index(index: int) -> Optional[str]:
    """Get the name of a move by its index."""
    if 0 <= index < len(ALL_MOVES):
        return ALL_MOVES[index].name
    return None

def get_move_index_by_name(name: str) -> Optional[int]:
    """Get the index of a move by name (handles both spaced and non-spaced names)."""
    normalized_search = normalize_move_name(name)
    for index, move in enumerate(ALL_MOVES):
        if normalize_move_name(move.name) == normalized_search:
            return index
    return None

def get_all_move_names() -> List[str]:
    """Get a list of all move names."""
    return [move.name for move in ALL_MOVES]


if __name__ == "__main__":
    print("\nAll Generation moves:")
    for i, move in enumerate(ALL_MOVES, 1):
        power_str = f"{move.power}" if move.power else "—"
        print(f"{i:3d}. {move.name:<15} | {move.type:<8} | {power_str:>3} | {move.accuracy:>3}% | {move.pp:>2} PP")