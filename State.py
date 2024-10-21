from enum import Enum


class State(Enum):
    Start = 0
    Letter = 1
    Digit = 2
    RelOperator = 3
    NotEqual = 6
    EnteringComment = 7
    InComment = 8
    ExitingComment = 9
    Slash = 10
