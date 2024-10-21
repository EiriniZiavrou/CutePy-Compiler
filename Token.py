import Family


class Token:
    # type : (syntax or lex)
    word: str
    family: Family
    line: int
    columnStart: int
    columnEnd: int

    def __init__(self, word: str, family: Family, line: int, columnStart: int, columnEnd: int):
        self.word = word
        self.family = family
        self.line = line
        self.columnStart = columnStart
        self.columnEnd = columnEnd

    def __str__(self):
        return f"Token: {self.word} of family {self.family} at line {self.line} from column {self.columnStart} to {self.columnEnd}"
