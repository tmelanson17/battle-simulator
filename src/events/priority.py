import random 

MAX_PRIORITY=8
MIN_PRIORITY=-6

class Priority:
    def __init__(self, bracket: int, speed: int):
        self.bracket = bracket
        self.speed = speed

    def __lt__(self, other: 'Priority') -> bool:
        # Speed tie resolution.
        if self == other:
            return random.random() > 0.5
        else:
            return (self.bracket, self.speed) > (other.bracket, other.speed)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise TypeError("Comparisons should be between Priority instances.")
        return (self.bracket, self.speed) == (other.bracket, other.speed)