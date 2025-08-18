import random 

class Priority:
    def __init__(self, turn: int, bracket: int, speed: int):
        self.turn = turn
        self.bracket = bracket
        self.speed = speed

    def __lt__(self, other: 'Priority') -> bool:
        # Speed tie resolution.
        if self == other:
            return random.random() > 0.5
        if self.turn != other.turn:
            return self.turn < other.turn
        else:
            return (self.bracket, self.speed) > (other.bracket, other.speed)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise TypeError("Comparisons should be between Priority instances.")
        return (self.turn, self.bracket, self.speed) == (other.turn, other.bracket, other.speed)