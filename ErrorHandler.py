from Family import Family


class ErrorHandler():
    def reportError(self, filePath, token, message):
        self.report(filePath, token, message, True)

    def reportWarning(self, filePath, token, message):
        self.report(filePath, token, message, False)

    def report(self, filePath, token, message, isError: bool):
        startIndex = token.columnStart
        endIndex = token.columnEnd
        if (token.family == Family.EOF): endIndex += 1
        lineNumber = token.line
        length = endIndex - startIndex
        print(f"Error in file {filePath}" if isError else f"Warning in file {filePath}")
        print(f"Error at line {lineNumber} at character {startIndex}:" if isError else f"Warning at line {lineNumber} at character {startIndex}:")
        print(f"{message}")
        print(f"{self.getLine(filePath, lineNumber)}")
        print(f"{' ' *(startIndex-1)}{'^'*length}")
        print()

    def getLine(self, filePath, lineNumber):
        with open(filePath, "r") as file:
            for _ in range(lineNumber-1):
                file.readline()
            return file.readline().rstrip('\n')
