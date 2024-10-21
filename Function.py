from typing import List
from Procedure import Procedure
from FormalParameter import FormalParameter


class Function(Procedure):

    def __init__(self, name: str, startingQuad: int, framelength: int, formalParameters: List[FormalParameter]):
        super().__init__(name, startingQuad, framelength, formalParameters)

    def __str__(self):
        return f"Function: {self.name} with starting quad {self.startingQuad}, framelength {self.framelength} and formal parameters {self.formalParameters}"
