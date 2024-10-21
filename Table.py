from typing import List
from Scope import Scope


class Table:
    scopes: List[Scope]

    def __init__(self):
        self.scopes = []
