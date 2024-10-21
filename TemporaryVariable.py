from Variable import Variable


class TemporaryVariable(Variable):
    
    def __init__(self, name: str, offset: int):
        super().__init__(name, offset)

    def __str__(self):
        return f"Temporary Variable: {self.name} with offset {self.offset}"
