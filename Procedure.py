from typing import List
from Entity import Entity
from FormalParameter import FormalParameter


class Procedure(Entity):
    startingQuad: int
    framelength: int
    formalParameters: List[FormalParameter]

    def __init__(self, name: str, startingQuad: int, framelength: int, formalParameters: List[FormalParameter]):
        super().__init__(name)
        self.startingQuad = startingQuad
        self.framelength = framelength
        self.formalParameters = formalParameters
    
    def __str__(self):
        return f"Procedure: {self.name} with starting quad {self.startingQuad}, framelength {self.framelength} and formal parameters {self.formalParameters}"
