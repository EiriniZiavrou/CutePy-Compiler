from enum import Enum


class Family(Enum):
    Error = -1
    Keyword = 0
    Identifier = 1
    DigitSequence = 2
    AddOperator = 3
    MulOperator = 4
    RelativeOperator = 5
    AssignmentOperator = 6
    Delimiter = 7
    GroupSymbol = 8
    Comment = 9
    EOF = 10
