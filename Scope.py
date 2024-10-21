from typing import List

from Entity import Entity


class Scope:
    level: int
    entities: List[Entity]

    def __init__(self, level):
        self.level = level
        self.entities = []
