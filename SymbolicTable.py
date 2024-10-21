from typing import Tuple
from Entity import Entity
from Parameter import Parameter
from Procedure import Procedure
from Scope import Scope
from Table import Table
from Variable import Variable


class SymbolicTable:
    table: Table
    fileName: str

    def __init__(self, fileName):
        self.table = Table()
        mainScope = Scope(0)
        self.table.scopes.append(mainScope)
        self.fileName = fileName.split('.')[0] + ".sym"
        open(self.fileName, 'w') #clear file

    def insert(self, entity: Entity):
        '''Inserts an entity in the current scope of the symbol table'''
        if (isinstance(entity, Procedure)):
            searchRes = self.search(entity.name, False)
            if ( searchRes!= None):
                if (isinstance(searchRes[0], Procedure)):
                    print(f"Function '{entity.name}' with parameters {entity.formalParameters} already exists in the symbol table, Cant add it again.\nTerminating Compiler")
                    exit(0)
        currentScope = self.table.scopes[-1]
        if (isinstance(entity, Variable)):
            searchRes = self.search(entity.name, False)
            if ( searchRes!= None):
                if (isinstance(searchRes[0], Variable)):
                    print(f"Variable '{entity.name}' already exists in this scope (Scope {currentScope.level}), Cant add it again.\nTerminating Compiler")
                    exit(0)
        currentScope.entities.append(entity)

    def addScope(self):
        '''Adds a new scope in the symbol table'''
        currentScope = self.table.scopes[-1]
        newScope = Scope(currentScope.level + 1)
        self.table.scopes.append(newScope)

    def search(self, name: str, printError = True) -> Tuple[Entity, int]:
        '''Searches for an entity in the symbol table
        Returns a tuple with the entity and the offset from the current scope'''
        tempScopes = self.table.scopes[:] #aparently this is the way to deep copy a list, man fuck python
        tempScopes.reverse()
        for scope in tempScopes:
            for entity in scope.entities:
                if entity.name == name:
                    return (entity, self.table.scopes[-1].level - scope.level)
        if (printError):
            print(f"Error: Entity {name} not found in symbol table (Current Scope = {self.table.scopes[-1].level})")
            self.printCurrentSymTable()
        return None

    def searchGlobalEntity(self, name:str) -> Entity:
        for entity in self.table.scopes[0].entities:
                if entity.name == name:
                    return entity
        print(f"Error: Entity {name} not found in symbol table's Scope 0")
        self.printCurrentSymTable()
        return None

    def deleteHighestLevelScope(self):
        self.outputSymTableToFile()
        self.table.scopes.pop()

    def getCurrentScope(self):
        return self.table.scopes[-1]

    def getMostLastCreatedEntity(self):
        return self.table.scopes[-1].entities[-1]

    def addParameterToMostRecentFunction(self, parameter: Parameter):
        function = self.getMostLastCreatedEntity()
        function.formalParameters.append(parameter)

    def outputSymTableToFile(self):
        with open(self.fileName, 'a') as file:
            for scope in self.table.scopes:
                file.write(f"Scope level {scope.level}:\n")
                for entity in scope.entities:
                    file.write(str(entity) + "\n")
            file.write("-----------------\n\n")

    def printCurrentSymTable(self):
        print(f"Number of Scopes: {len(self.table.scopes)}")
        for scope in self.table.scopes:
            print(f"Scope level {scope.level}:")
            for entity in scope.entities:
                    print(str(entity) + "")
        print("-----------------\n")
