from typing import List
from Quad import Quad


class IntermiadeCodeGenerator():
    latestQuadNumber = 0
    latestTempNumber = 0
    listOfQuads : List[Quad]
    fileName = ""

    def __init__(self, fileName) -> None:
        self.listOfQuads = self.emptyList()
        self.fileName = fileName.split('.')[0] + ".int"
        open(self.fileName, 'w') #clear file

    def nextQuad(self):
        return self.latestQuadNumber + 1

    def genQuad(self, op, x, y, z):
        quad = Quad(self.nextQuad(), op, x, y, z)
        self.latestQuadNumber += 1
        self.listOfQuads.append(quad)
        return quad

    def newTemp(self):
        temp = self.latestTempNumber
        self.latestTempNumber += 1
        return f"T_{temp}"

    def emptyList(self):
        return []

    def makeList(self, x):
        return [x]

    def merge(self, p1, p2):
        return p1 + p2

    def backPatch(self, list, z):
        for quadNumber in list:
            matching_quad = next((quad for quad in self.listOfQuads if quad.number == quadNumber), None)
            if matching_quad is not None:
                matching_quad.z = z

    def printAllQuads(self):
        for quad in self.listOfQuads:
            print(quad)

    def outputToFile(self):
        with open(self.fileName, 'w') as file:
            for quad in self.listOfQuads:
                file.write(str(quad) + "\n")
