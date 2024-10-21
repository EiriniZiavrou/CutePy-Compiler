class Quad:
    number: int
    op: str
    x: str
    y: str
    z: str

    def __init__(self, number: int, op: str, x: str, y: str, z: str):
        self.number = number
        self.op = op
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        xStr = f" {self.x}" if self.x != None else " _"#dont print _
        yStr = f" {self.y}" if self.y != None else " _"
        zStr = f" {self.z}" if self.z != None else " _"
        return f"{self.number}: {self.op}{xStr}{yStr}{zStr}"
