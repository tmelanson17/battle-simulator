# Calculates the raw HP of a pokemon based on its base stats, level, IVs, and EVs.
def calculate_hp(base: int, level: int = 100, iv: int = 0, ev: int = 0) -> int:
    return int(((base * 2 + iv + (ev // 4)) * level) / 100) + level + 10


def calculate_other_stat(base: int, level: int = 100, iv: int = 0, ev: int = 0) -> int:
    return int(((base * 2 + iv + (ev // 4)) * level) / 100) + 5
