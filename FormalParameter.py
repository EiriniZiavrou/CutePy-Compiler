from Entity import Entity


class FormalParameter(Entity):
    mode: str

    def __init__(self, name: str, mode:str):
        Entity.__init__(self, name)
        self.mode = mode

    def __str__(self):
        return f"Formal Parameter: {self.name}"
    
    __repr__ = __str__
