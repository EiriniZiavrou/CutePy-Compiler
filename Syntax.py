from typing import List, Tuple
from Token import Token
from ErrorHandler import ErrorHandler
from Family import Family
from FinalCodeGenerator import FinalCodeGenerator
from FormalParameter import FormalParameter
from Function import Function
from GlobalVariable import GlobalVariable
from IntermiadeCodeGenerator import IntermiadeCodeGenerator
from Lex import Lex
from Parameter import Parameter
from Procedure import Procedure
from SymbolicTable import SymbolicTable
from TemporaryVariable import TemporaryVariable
from Variable import Variable


class Syntax():
    token: Token
    fileName = ""
    hasError = False
    lex: Lex
    icg: IntermiadeCodeGenerator
    fcg: FinalCodeGenerator
    symbolicTable: SymbolicTable
    currentOffset = 12
    numberOfGlobalVars = 0
    isDeclaringGlobal = True

    def __init__(self, fileNamePath: str):
        global fileName
        global lex
        global icg
        global symbolicTable
        global fcg
        lex = Lex(fileNamePath)
        fileName = fileNamePath
        icg = IntermiadeCodeGenerator(fileName)
        symbolicTable = SymbolicTable(fileName)
        fcg = FinalCodeGenerator(fileName, symbolicTable)

    def getSyntaxHasError(self) -> bool:
        global hasError
        return self.hasError

    def startRule(self):
        '''
        If this is called no tokens have been read
        Ends at EOF
        '''
        global fcg
        self.declarations()
        while (self.isWord("def", False)): self.defFunction()
        self.defMainPart()
        self.callMainPart()

    def defMainPart(self):
        '''
        If this is called token is #def
        Does not consume any extra token
        '''
        global token
        if (self.isWord("#def", False)):
            self.defMainFunction()
        else: return

    def defMainFunction(self):
        '''
        If this is called token is #def
        Does not consume any extra token
        '''
        global token
        token = lex.getNextToken()
        self.isWord("main")     

    def defFunction(self):
        '''
        Is called if token is "def"
        Consumes 1 extra
        '''
        global token
        global symbolicTable
        global fcg
        self.isDeclaringGlobal = False
        self.currentOffset  = 12
        functionFramelength = 12
        token = lex.getNextToken()
        if (self.isFamily(Family.Identifier)):
            blockName = token.word
            print(f"Creating Symbol Table/Intermiade Code for {blockName}")
            symbolicTable.insert(Function(blockName, 0, 12, []))
            token = lex.getNextToken()
            if (self.isWord("(")):
                self.idList()
                functionEntity : Function = symbolicTable.getMostLastCreatedEntity()
                symbolicTable.addScope()
                for parameter in functionEntity.formalParameters: 
                    symbolicTable.insert(Parameter(parameter.name, self.currentOffset, parameter.mode))
                    self.currentOffset += 4
                    functionFramelength += 4
                if (self.isWord(")")):
                    token = lex.getNextToken()
                    if (self.isWord(":")):
                        token = lex.getNextToken()
                        if (self.isWord("#{")):
                            self.declarations()
                            while (self.isWord("def", False)): self.defFunction()
                            startQuad = icg.genQuad("begin_block", blockName, None, None)
                            functionEntity.startingQuad = icg.nextQuad()
                            self.statements()
                            functionEntity.framelength = self.currentOffset
                            if (self.isWord("#}")): token = lex.getNextToken()
                            endQuad = icg.genQuad("end_block", blockName, None, None)
                            icg.outputToFile()
                            print(f"Creating Final Code for {blockName}")
                            fcg.generateFinalCode(startQuad.number, endQuad.number)
                            symbolicTable.deleteHighestLevelScope()

    def declarations(self):
        '''
        Is called with no knowlegde of the current token.
        Consumes 1 extra
        '''
        global token
        token = lex.getNextToken()
        while (self.isWord("#int", False)): self.declarationLine()

    def declarationLine(self):
        '''
        Is called if token is #int
        Consumes 1 extra
        '''
        global token
        self.idList()

    def statement(self):
        '''
        If we have entered token is keyword or identifier
        Consumes 1 extra token

        Returns: The number of the quad of the statement
        '''
        global token
        if (self.isWord("if", False) or self.isWord("while", False)): self.structuredStatement()
        elif (self.isWord("print", False) or self.isWord("return", False) or self.isWord("global", False) or self.isFamily(Family.Identifier, False)): self.simpleStatement()

    def statements(self):
        '''
        If this is called token is a keyword or identifier or neither
        Consumes 1 extra token

        Returns: The number of the quad of the statement
        '''
        global token
        keywords = ["print", "return", "if", "while", "global"]
        while (token.word in keywords or self.isFamily(Family.Identifier, False)):
            self.statement()
            if (token == None): return

    def simpleStatement(self):
        '''
        If this is called token is print, return, global or an identifier
        Consumes 1 extra token
        '''
        global token
        if self.isWord("print", False): self.printStat()
        elif self.isWord("return", False): self.returnStat()
        elif self.isWord("global", False): self.globalStat()
        elif self.isFamily(Family.Identifier, False): self.assignmentStat()

    def structuredStatement(self):
        '''
        If we have entered token is while or if
        Consumes 1 extra token
        '''
        global token
        if self.isWord("if", False): self.ifStat()
        elif self.isWord("while", False): self.whileStat()

    def globalStat(self) -> int:
        '''
        If this is called token is global
        Consumes 1 extra token
        '''
        global token
        self.idList()

    def assignmentStat(self) -> int:
        '''
        If this is called token is an identifier
        Consumes 1 extra token
        '''
        global token
        targetVariable = token.word
        token = lex.getNextToken()
        if self.isFamily(Family.AssignmentOperator):
            token = lex.getNextToken()
            if (not self.isWord("int", False)):
                expr = self.expression()
                quad = icg.genQuad(":=", expr, None, targetVariable)
            else:
                token = lex.getNextToken()
                if self.isWord("("):
                    token = lex.getNextToken()
                    if self.isWord("input"):
                        token = lex.getNextToken()
                        if self.isWord("("):
                            token = lex.getNextToken()
                            if self.isWord(")"):
                                token = lex.getNextToken()
                                if self.isWord(")"):
                                    token = lex.getNextToken()
                                    quad = icg.genQuad("in", targetVariable, None, None)
            return quad.number

    def printStat(self):
        '''
        If this is called token is print
        Consumes 1 extra token
        '''
        global token
        token = lex.getNextToken()
        if self.isWord("("):
            token = lex.getNextToken()
            expr = self.expression()
            if self.isWord(")"):
                token = lex.getNextToken()
                quad = icg.genQuad("out", expr, None, None)
                return quad.number

    def returnStat(self):
        '''
        If this is called token is return
        Consumes 1 extra token
        '''
        global token
        global icg
        token = lex.getNextToken()
        expr = self.expression()
        icg.genQuad("ret", None, None, expr)

    def ifStat(self):
        '''
        If we have entered token is if or elif
        Consumes 1 extra token
        '''
        global token
        token = lex.getNextToken()
        (resTrue, resFalse) = self.condition()
        if self.isWord(':'):
            token = lex.getNextToken()
            icg.backPatch(resTrue, icg.nextQuad())
            if (self.isWord('#{', False)):
                token = lex.getNextToken()
                print("finding statements")
                self.statements()
                if self.isWord('#}'):
                    token = lex.getNextToken()
            else:
                self.statement()
            ifList = icg.makeList(icg.nextQuad())
            icg.genQuad("jump", None, None, "_")
            icg.backPatch(resFalse, icg.nextQuad())
            self.elseStat()
            icg.backPatch(ifList, icg.nextQuad())

    def elseStat(self):
        '''
        If this is called token is elif or else or neither
        Consumes 1 extra token
        '''
        global token
        if (self.isWord('elif', False)):
            self.ifStat()
        elif (self.isWord('else', False)):
            token = lex.getNextToken()
            if self.isWord(':'):
                token = lex.getNextToken()
                if (not self.isWord('#{', False)):
                    self.statement()
                else:
                    self.statements()
                    token = lex.getNextToken()
                    if self.isWord('#}'): token = lex.getNextToken()
        else: return

    def whileStat(self):
        '''
        If this is called token is while
        Consumes 1 extra token
        '''
        global token
        global icg
        token = lex.getNextToken()
        condLabel = icg.nextQuad()
        (condTrue, condFalse) = self.condition()
        if (self.isWord(':')):
            icg.backPatch(condTrue, icg.nextQuad())
            token = lex.getNextToken()
            if (self.isWord('#{', False)):
                self.declarations()
                self.statements()
                if self.isWord('#}'): token = lex.getNextToken()
            else:
                self.statement()
            icg.genQuad("jump", None, None, condLabel)
            icg.backPatch(condFalse, icg.nextQuad())

    def idList(self):
        '''
        Is called if token is #int or global or ( after function name
        Consumes 1 extra
        '''
        global token
        global symbolicTable
        global currentOffset
        word = token.word
        token = lex.getNextToken()
        if (self.isFamily(Family.Identifier, False)):
            if (self.isDeclaringGlobal): self.numberOfGlobalVars += 1
            parameterName = token.word
            if  word == "#int": 
                symbolicTable.insert(Variable(parameterName,self.currentOffset))
                self.currentOffset += 4
            elif word == "(": symbolicTable.addParameterToMostRecentFunction(FormalParameter(parameterName, "REF"))
            elif word == "global": symbolicTable.insert(GlobalVariable(parameterName))
            token = lex.getNextToken()
            while (self.isWord(",", False)):
                token = lex.getNextToken()
                if (self.isFamily(Family.Identifier)):
                    if (self.isDeclaringGlobal): self.numberOfGlobalVars += 1
                    parameterName = token.word
                    if  word == "#int": 
                        symbolicTable.insert(Variable(parameterName,self.currentOffset))
                        self.currentOffset += 4
                    elif word == "(": symbolicTable.addParameterToMostRecentFunction(FormalParameter(parameterName, "REF"))
                    elif word == "global": symbolicTable.insert(GlobalVariable(parameterName))
                    token = lex.getNextToken()
        else: return

    def expression(self) -> str:
        '''
        If this is called token is the first token of the expression
        Consumes 1 extra token

        Returns: The name of the temp variable that holds the result of the expression
        '''
        global token
        global icg
        global symbolicTable
        sign = self.optionalSign()
        term1 = self.term()
        if (sign != None):
            w = icg.newTemp()
            symbolicTable.insert(TemporaryVariable(w, self.currentOffset))
            self.currentOffset += 4
            icg.genQuad(sign, 0, term1, w)
            term1 = w
        while (self.isFamily(Family.AddOperator, False)):
            operator = token.word
            token = lex.getNextToken()
            term2 = self.term()
            w = icg.newTemp()
            symbolicTable.insert(TemporaryVariable(w, self.currentOffset))
            self.currentOffset += 4
            icg.genQuad(operator, term1, term2, w)
            term1 = w
        return term1

    def term(self) -> str:
        '''
        If this is called token is the first token of the term
        Consumes 1 extra token

        Returns: The name of the temp variable that holds the result of the expression
        '''
        global token
        global icg
        factor1 = self.factor()
        while (self.isFamily(Family.MulOperator, False)):
            operator = token.word
            token = lex.getNextToken()
            factor2 = self.factor()
            w = icg.newTemp()
            symbolicTable.insert(TemporaryVariable(w, self.currentOffset))
            self.currentOffset += 4
            icg.genQuad(operator, factor1, factor2, w)
            factor1 = w
        return factor1

    def factor(self) -> str:
        '''
        If this is called token is the first token of the factor
        Consumes 1 extra token

        Returns: The name of the temp variable that holds the result of the expression
        '''
        global token
        global icg
        global symbolicTable
        if (self.isFamily(Family.DigitSequence, False)):
            number = token.word
            token = lex.getNextToken() #One extra to account for idTail
            return number
        elif self.isWord("(", False):
            token = lex.getNextToken()
            expr = self.expression()
            if self.isWord(")"):
                token = lex.getNextToken() #One extra to account for idTail
                return expr
        elif self.isFamily(Family.Identifier):
            identifier = token.word
            methodReturn = self.idTail()
            if (methodReturn != None): 
                identifier = methodReturn
                symbolicTable.insert(TemporaryVariable(identifier, self.currentOffset))
                self.currentOffset += 4
            return identifier

    def idTail(self):
        '''
        If this is called token is an Identifier
        Consumes 1 extra token
        '''
        global token
        global icg
        functionName = token.word
        token = lex.getNextToken()
        if (self.isWord("(", False)):
            parQuadsLabels = self.actualParList()
            if (parQuadsLabels != None): icg.backPatch(parQuadsLabels, functionName)
            if self.isWord(")"):
                token = lex.getNextToken()
                temp = icg.newTemp()
                icg.genQuad("par", temp, "RET", functionName)
                icg.genQuad("call", functionName, None, None)
                return temp
        else: return None

    def actualParList(self):
        '''
        If this is called token is (
        Consumes 1 extra token
        '''
        global token
        global icg
        token = lex.getNextToken()
        if (self.isWord(")", False)): return
        expr = self.expression()
        parListQuads = []
        if (expr[0] in "0123456789"): quad = icg.genQuad("par", expr, "VAL", None)
        else : quad = icg.genQuad("par", expr, "REF", None)
        parListQuads.append(quad.number)
        while (self.isWord(",", False)):
            token = lex.getNextToken()
            expr = self.expression()
            if (expr[0] in "0123456789"): quad = icg.genQuad("par", expr, "VAL", None)
            else : quad = icg.genQuad("par", expr, "REF", None)
            parListQuads.append(quad.number)
        return parListQuads

    def optionalSign(self):
        '''
        If this is called the token is -, + or digit
        Consumes 1 extra token
        '''
        global token
        global icg
        if (self.isFamily(Family.AddOperator, False)):
            op = token.word
            token = lex.getNextToken()
            return op
        else: return None

    def condition(self) -> Tuple[List[int], List[int]]:
        '''
        If we have entered token is the first term of the condition
        Consumes 1 extra token
        '''
        global token
        global icg
        resTrue = icg.emptyList()
        resFalse = icg.emptyList()
        (term1True, term1False) = self.boolTerm()
        resTrue = term1True
        resFalse = term1False
        while (self.isWord("or", False)):
            icg.backPatch(resFalse, icg.nextQuad())
            token = lex.getNextToken()
            (term2True, term2False) = self.boolTerm()
            resTrue = icg.merge(resTrue, term2True)
            resFalse = term2False
        return (resTrue, resFalse)

    def boolTerm(self) -> Tuple[List[int], List[int]]:
        '''
        If we have entered token is the first term of the boolTerm
        Consumes 1 extra token
        '''
        global token
        global icg
        resTrue = icg.emptyList()
        resFalse = icg.emptyList()
        (factor1True, factor1False) =  self.boolFactor()
        resTrue = factor1True
        resFalse = factor1False
        while (self.isWord("and", False)):
            icg.backPatch(resTrue, icg.nextQuad())
            token = lex.getNextToken()
            (factor2True, factor2False) = self.boolFactor()
            resTrue = factor2True
            resFalse = icg.merge(resFalse, factor2False)
        return (resTrue, resFalse)

    def boolFactor(self) -> Tuple[List[int], List[int]]:
        '''
        If we have entered token is the first term of the factor
        Consumes 1 extra token
        '''
        global token
        if (self.isWord('not', False)):
            token = lex.getNextToken()
            if (self.isWord("(", False)):
                token = lex.getNextToken()
                (condTrue, condFalse) = self.condition()
                if (self.isWord(")")):
                    token = lex.getNextToken()
                    return (condFalse, condTrue)
        elif (self.isWord("(", False)):
            token = lex.getNextToken()
            (condTrue, condFalse) = self.condition()
            if (self.isWord(")")):
                token = lex.getNextToken()
                return (condTrue, condFalse)
        else:
            exrp1 = self.expression()
            if (self.isFamily(Family.RelativeOperator, False)):
                op = token.word
                token = lex.getNextToken()
                expr2 = self.expression()
                resTrue = icg.makeList(icg.nextQuad())
                icg.genQuad(op, exrp1, expr2, "_")
                resFalse = icg.makeList(icg.nextQuad())
                icg.genQuad("jump", None, None, "_")
                return (resTrue, resFalse)

    def callMainPart(self):
        '''
        If this is called token in main
        Ends at EOF
        '''
        global token
        global icg
        global symbolicTable
        global fcg
        # print(f"reached main wth {self.numberOfGlobalVars} globals declared")
        self.currentOffset = 12 + (self.numberOfGlobalVars * 4)
        self.declarations()
        print(f"Creating Symbol Table/Intermiade Code for main")
        symbolicTable.insert(Procedure("main", icg.nextQuad()+1, 12, []))
        procedureEntity = symbolicTable.getMostLastCreatedEntity()
        while (self.isWord("def", False)): self.defFunction()
        startQuad = icg.genQuad("begin_block", "main", None, None)
        self.statements()
        icg.genQuad("halt", None, None, None)
        endQuad = icg.genQuad("end_block", "main", None, None)
        icg.outputToFile()
        procedureEntity.framelength = self.currentOffset
        print(f"Creating Final Code for main")
        fcg.generateFinalCode(startQuad.number, endQuad.number)
        symbolicTable.outputSymTableToFile()
        self.isFamily(Family.EOF)

    def isWord(self, word: str, isStrictMatch: bool = True) -> bool:
        global token
        global hasError
        global fileName
        if token.word != word:
            if isStrictMatch:
                self.hasError = True
                tokenWord = token.word if token.family != Family.EOF else "EOF"
                ErrorHandler().reportError(fileName, token, f"Expected {word}, got {tokenWord}")
            return False
        return True

    def isFamily(self, family: Family, isStrictMatch: bool = True) -> bool:
        global token
        global hasError
        global fileName
        if token.family != family:
            if isStrictMatch:
                self.hasError = True
                ErrorHandler().reportError(fileName, token, f"Expected {family}, got {token.family}")
            return False
        return True
