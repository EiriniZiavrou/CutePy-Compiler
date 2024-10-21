import Entity


class SymbolicConstant(Entity):
    value: int

    def __init__(self, name: str, value: int):
        super().__init__(name)
        self.value = value

    def __str__(self):
        return f"Constant: {self.name} with value {self.value}"
