import string
from typing import Optional, Tuple
from ErrorHandler import ErrorHandler
from State import State
from Token import Token
from Family import Family

class Lex():
    currentState: State

    word = ""
    filePath = ""
    currentFileLocation = 0
    currentLine = 1
    currentColumn = 1

    def __init__(self, fullFilePath: str):
        """
        This function initializes the file path, Needed before anything calls to lex.

        Parameters:
        fullFilePath (string): The path of the file
        """
        global filePath
        self.filePath = fullFilePath

    def getNextToken(self) -> Optional[Token]:
        """
        This function returns the next word token with the family it belongs in.
        Requirement: Init() must be called before calling this function.

        Returns:
        A token
        """
        # global filePath
        if (self.filePath == ""):
            raise RuntimeError("Error: File path not set, call Init() first")
        global currentFileLocation
        global currentLine
        global currentColumn
        with (open(self.filePath, 'r')) as file:
            file.seek(self.currentFileLocation)
            global currentState
            global word
            currentState = State.Start
            word = ""
            result = None
            while result == None:
                nextChar = file.read(1)
                self.currentColumn += 1
                column = self.currentColumn
                result = self.processNextChar(nextChar)
                # if (len(word) > 30):
                #     word = word[:30]
                if (nextChar == "\n"):
                    self.currentLine += 1
                    self.currentColumn = 1
            if result[2] and nextChar != "":
                file.seek(file.tell() - 1)
                self.currentColumn -= 1
                if (nextChar == "\n"):
                    self.currentLine -= 1
                    self.currentColumn = column
                column = self.currentColumn
            self.currentFileLocation = file.tell()
            # print(f"Word: \"{result[0]}\", Family: {result[1]}, Line: {self.currentLine}, Column: {column}")
            # ErrorHandler().reportWarning(self.filePath, Token(result[0], result[1], self.currentLine, column - len(result[0]), column), f"Word is: \"{result[0]}\"")
            return Token(result[0], result[1], self.currentLine, column - len(result[0]), column)


    def processNextChar(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        """
        This function processes the next character and returns the token and it's family if it's a valid token.
        It is supposed tobe called by lex() only, and should not be called by any other function.

        Parameters:
        nextChar (string): The next character to process, must be exactly 1 character.

        Returns:
        If a final state is reached, it returns a tuple with the word token, it's family and if the file cursor should be moved 1 character back: (token, Family, bool)

        Else it returns None
        """
        global currentState
        global word
        global characters
        global digits
        global keywords
        # print (f"Current State: {currentState}, Next Char: {nextChar}")
        match (currentState, nextChar):
            case (State.Start, char):
                return self.processStartState(nextChar)
            case (State.ExitingComment, char):
                return self.processExitingComment(char)
            case (_, ""):#EOF while not in start
                return self.processNextChar(" ")
            case (State.RelOperator, char):
                return self.processRelativeOperator(char)
            case (State.Slash, "/"):
                return ("//", Family.MulOperator, False)
            case (State.Slash, _):
                return ("error after /", Family.Error, True)
            case (State.Letter, char):
                return self.processString(char)
            case (State.Digit, char):
                return self.processDigit(char)
            case (State.EnteringComment, char):
                return self.processEnteringComment(char)
            case (State.InComment, char):
                return self.processInComment(char)
            case (state, char):
                return (f"Error: State {state} with character {char}", Family.Error, True)

    def processStartState(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global currentState
        global word
        if currentState != State.Start:
            raise RuntimeError("Error: processStartState called when currentState is not Start")
        match nextChar:
            case "":
                return ("", Family.EOF, False)
            case char if char in " \n\t":
                pass
            case char if char in ",:()*%+-":
                return self.processSingleCharacter(char)
            case char if char in "<>=!":
                word = char
                currentState = State.RelOperator
            case '/':
                currentState = State.Slash
            case '#':
                currentState = State.EnteringComment
            case char if char in string.ascii_letters:
                word = char
                currentState = State.Letter
            case char if char in string.digits:
                word = char
                currentState = State.Digit
            case _:
                return ("Error at Start", Family.Error, False)

    def processSingleCharacter(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        if nextChar not in ",:()%*+-":
            raise RuntimeError(f"Error: processSingleCharacter called with invalid character \"{nextChar}\"")
        if nextChar in ",:": return (nextChar, Family.Delimiter, False)
        elif nextChar in "()": return (nextChar, Family.GroupSymbol, False)
        elif nextChar in "+-": return (nextChar, Family.AddOperator, False)
        return (nextChar, Family.MulOperator, False)

    def processRelativeOperator(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global word
        if nextChar == "=":
            return (word + "=", Family.RelativeOperator, False)
        if word == '!':
            return ("", Family.Error, True)
        if word == '=':
            return (word, Family.AssignmentOperator, True)
        return (word, Family.RelativeOperator, True)

    def processEnteringComment(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global currentState
        global word
        match nextChar:
            case char if (char in string.ascii_letters):
                word = "#" + nextChar
                currentState = State.Letter
            case char if (nextChar in "{}"):
                return ("#" + nextChar, Family.GroupSymbol, False)
            case "#":
                currentState = State.InComment
            case _:
                return ("", Family.Error, True)

    def processInComment(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global currentState
        if (nextChar == ""):
            return ("error in comment (EOF)", Family.Error, False)
        if (nextChar == "#"):
            currentState = State.ExitingComment

    def processExitingComment(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global currentState
        if (nextChar == "#"):
            currentState = State.Start
        else:
            return ("Error in Exiting Comment", Family.Error, True)

    def processString(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global word
        keywords = ["main", "def", "#def", "#int", "global", "if", "elif", "else", "while", "print", "return", "input", "int", "and", "or", "not"]
        charIsLetterOrDigit = (nextChar in string.ascii_letters) or (nextChar in string.digits)
        if (not charIsLetterOrDigit):
            if (len(word)>30):
                ErrorHandler().reportWarning(self.filePath, Token(word, Family.Identifier, self.currentLine, self.currentColumn - len(word)-1, self.currentColumn-1), f"Identifier '{word}' is longer than 30 characters, only the first 30 will be taken into account ('{word[:30]}')")
                word = word[:30]
            if word in keywords:
                return (word, Family.Keyword, True)
            return (word, Family.Identifier, True)
        word += nextChar

    def processDigit(self, nextChar: str) -> Optional[Tuple[str, Family, bool]]:
        global word
        if nextChar not in string.digits:
            oldNumber = int(word)
            oldWord = word
            number = 0
            wasOutOfBounds = False
            if oldNumber > 32767:
                wasOutOfBounds = True
                number = 32767
            elif oldNumber < -32767:
                wasOutOfBounds = True
                number = -32767
            else: number = oldNumber
            word = str(number)
            if wasOutOfBounds: ErrorHandler().reportWarning(self.filePath, Token(word, Family.DigitSequence, self.currentLine, self.currentColumn - len(oldWord) - 1, self.currentColumn-1), f" Number {oldNumber} was outside the bounds so it was set to {number}")
            return (word, Family.DigitSequence, True)
        word += nextChar
