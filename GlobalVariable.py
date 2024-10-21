from Entity import Entity


class GlobalVariable(Entity):
    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return f"Pseudo-Global-Variable: {self.name} "
 