from Entity import Entity


class Variable(Entity):
    offset: int

    def __init__(self, name: str, offset: int):
        super().__init__(name)
        self.offset = offset

    def __str__(self):
        return f"Variable: {self.name} with offset {self.offset}"
