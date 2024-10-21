from FormalParameter import FormalParameter
from Variable import Variable


class Parameter(FormalParameter, Variable):
    
    def __init__(self, name: str, offset: int, mode: str):
        super().__init__(name, mode)
        self.offset = offset

    def __str__(self):
        return f"Parameter: {self.name} and offset {self.offset}"
