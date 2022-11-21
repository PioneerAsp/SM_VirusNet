from enum import Enum

class State(Enum):
    # Computer State
    RESISTANT = 0
    SUSCEPTIBLE = 1
    INFECTED = 2
    DEAD = 3
    # Virus State
    WEAK = 4
    REGULAR = 5
    MODERATE = 6
    MORTAL = 7