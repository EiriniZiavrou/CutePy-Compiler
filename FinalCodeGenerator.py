from GlobalVariable import GlobalVariable
from Parameter import Parameter
from SymbolicTable import SymbolicTable
from TemporaryVariable import TemporaryVariable
from Variable import Variable


class FinalCodeGenerator():
    intCodeFileName = ""
    finalCodeFileName = ""
    symbolicTable: SymbolicTable
    functionsAndTheirLevels = {"main": 0}

    def __init__(self, fileName: str, symbolicTable: SymbolicTable):
        self.intCodeFileName = fileName.split('.')[0] + ".int" #get the int code created by icg
        self.finalCodeFileName = fileName.split('.')[0] + ".asm"
        open(self.finalCodeFileName, 'w') #clear the file
        self.symbolicTable = symbolicTable
        self.produce(".data", True)
        self.produce("strNewline: .ascii \"\\n\"")
        self.produce(".text", True)
        self.produce("L0:", True)
        self.produce("j main")

    def gnlvcode(self, variable):
        result = self.symbolicTable.search(variable)
        if (result == None): 
            print("Terminating Compiler") 
            exit(0)
        (variableEntity, offset) = result
        self.produce("lw t0, -4(sp)")
        for _ in range(offset-1):
            self.produce("lw t0, -4(t0)")
        self.produce(f"addi t0, t0, -{variableEntity.offset}")
            
    def loadVariable(self, variable, register):
        if (variable[0] in "0123456789"):
            num = int(variable)
            self.produce(f"li {register}, {num}")
            return
        result = self.symbolicTable.search(variable)
        if (result == None): 
            print("Terminating Compiler (loadVariable)") 
            exit(0)
        (variableEntity, offset) = result
        if (offset == 0):
            if isinstance(variableEntity,GlobalVariable): #globalVar
                actualGlobalVar = self.symbolicTable.searchGlobalEntity(variable)
                if (actualGlobalVar == None):
                    print("Terminating Compiler (loadVariable)") 
                    exit(0)
                self.produce(f"lw {register}, -{actualGlobalVar.offset}(gp)")
            if isinstance(variableEntity,Parameter) and variableEntity.mode == "VAL": #local var/parameter
                self.produce(f"#{variableEntity} (with Scope offset {offset})")
                self.produce(f"lw t0, -{variableEntity.offset}(sp)")
            elif isinstance(variableEntity,Variable) or isinstance(variableEntity,TemporaryVariable) or (isinstance(variableEntity,Parameter) and variableEntity.mode == "REF"):
                self.produce(f"#{variableEntity} (with Scope offset {offset})")
                self.produce(f"lw {register}, -{variableEntity.offset}(sp)")
        elif (offset < self.symbolicTable.getCurrentScope().level): #variable/parameter is in ancestor of current scope
            if (isinstance(variableEntity,Parameter) and variableEntity.mode == "REF"):
                self.gnlvcode(variable)
                self.produce(f"lw t0, 0(t0)")
                self.produce(f"lw {register}, 0(t0)")
            elif (isinstance(variableEntity,Variable) or (isinstance(variableEntity,Parameter) and variableEntity.mode == "VAL")):
                self.gnlvcode(variable)
                self.produce(f"lw {register}, 0(t0)")
        else:
            return True #to check in generateFinalCode to also display the line, not perfect I know

    def storeVariable(self, variable, register):
        if (variable[0] in "0123456789"):
            num = int(variable)
            self.loadVariable(num, "t0")
            self.storeVariable("t0", register)
            return
        result = self.symbolicTable.search(variable)
        if (result == None): 
            print("Terminating Compiler (storeVariable)") 
            exit(0)
        (variableEntity, offset) = result
        if (offset == 0):
            if isinstance(variableEntity,GlobalVariable): #globalVar
                actualGlobalVar = self.symbolicTable.searchGlobalEntity(variable)
                if (actualGlobalVar == None):
                    print("Terminating Compiler (loadVariable)") 
                    exit(0)
                self.produce(f"sw {register}, -{actualGlobalVar.offset}(gp)")
            elif isinstance(variableEntity,Parameter) and variableEntity.mode == "VAL":
                self.produce(f"lw t0, -{variableEntity.offset}(sp)")
                self.produce(f"sw {register}, 0(t0)")
            elif isinstance(variableEntity,Variable) or isinstance(variableEntity,TemporaryVariable) or (isinstance(variableEntity,Parameter) and variableEntity.mode == "VAL"):
                self.produce(f"sw {register}, -{variableEntity.offset}(sp)")      
        elif (offset < self.symbolicTable.getCurrentScope().level):
            if (isinstance(variableEntity,Parameter) and variableEntity.mode == "REF"):
                self.gnlvcode(variable)
                self.produce(f"lw t0, 0(t0)")
                self.produce(f"sw {register}, 0(t0)")
            elif (isinstance(variableEntity,Variable) or (isinstance(variableEntity,Parameter) and variableEntity.mode == "REF")):
                self.gnlvcode(variable)
                self.produce("lw t0, 0(t0)")
                self.produce(f"sw {register}, 0(t0)")     
        else:
            return True #to check in generateFinalCode to also display the line, not perfect I know

    def produce(self, codeLine: str, isLabel : bool = False):
        '''Write a line of code to the final code file'''
        with open(self.finalCodeFileName, 'a') as file:
            if (isLabel): file.write(f"{codeLine}\n")
            else: file.write(f"\t{codeLine}\n")

    def generateFinalCode(self, startLabel, endLabel):
        currentParameterIndex = 0
        isFirstPar = True
        currentFunction = ""
        with open(self.intCodeFileName, 'r') as file:
            for line in file:
                parts = line.split()
                label = parts[0]
                if (int(label.removesuffix(":")) < startLabel or int(label.removesuffix(":")) > endLabel): continue
                op = parts[1]
                x = parts[2]
                y = parts[3]
                z = parts[4]
                if (int(label.removesuffix(":")) == startLabel): 
                    currentFunction = x
                    self.functionsAndTheirLevels[currentFunction] = self.symbolicTable.getCurrentScope().level
                self.produce(f"L{label}", True)
                if (op in "+-*//%"):
                    self.produce("#Load x in t1")
                    if (self.loadVariable(x, "t1")): 
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    self.produce("#Load y in t2")
                    if (self.loadVariable(y, "t2")): 
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    opToCommand = {
                        "+": "add",
                        "-": "sub",
                        "*": "mul",
                        "//": "div",
                        "%": "rem"
                    }
                    self.produce("#Apply Operator to operants")
                    self.produce(f"{opToCommand[op]} t1, t2, t1")
                    self.produce("#Put Results in z")
                    self.storeVariable(z, "t1")
                elif (op == ":="):
                    self.produce("#Load x in t1")
                    if(self.loadVariable(x, "t1")):
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    self.produce("#Store t1 in z")
                    if(self.storeVariable(z, "t1")):
                        print(f"Variable {z} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                elif (op == "jump"):
                    self.produce("#Jump to z")
                    self.produce(f"j L{z}")
                elif (op in ["==", "!=", "<", ">", "<=", ">="]):
                    self.produce("#Load x in t1")
                    if (self.loadVariable(x, "t1")): 
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    self.produce("#Load y in t2")
                    if (self.loadVariable(y, "t2")): 
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    IntToFinalCorrelationTable = {
                        '==': "beq",
                        "!=": "bne",
                        "<": "blt",
                        ">": "bgt",
                        "<=": "ble",
                        ">=": "bge" 
                    }
                    actualOp = IntToFinalCorrelationTable[op]
                    self.produce("#Compare t1 and t2 branch if needed")
                    self.produce(f"{actualOp} t1, t2, L{z}")
                elif (op == "begin_block"):
                    self.produce(f"{x}:", True)
                    if (x == "main"):
                        functionFramelength = self.symbolicTable.search("main")[0].framelength
                        self.produce(f"#Add main function's framelength to sp")
                        self.produce(f"addi sp, sp, {functionFramelength}")
                        self.produce(f"#Move gp to sp")
                        self.produce("mv gp, sp")
                    else:
                        self.produce(f"#Store Current ra in 0(sp)")
                        self.produce("sw ra, 0(sp)")
                elif (op == "halt"):
                    self.produce("#Exit")
                    self.produce("li a0, 0")
                    self.produce("li a7, 93")
                    self.produce("ecall")
                elif (op == "par"):
                    if (isFirstPar): 
                        self.produce(f"#First par, so create fp of new func")
                        self.produce(f"addi fp, sp, {self.symbolicTable.search(z)[0].framelength}")
                        isFirstPar = False
                    if (y == "VAL"):
                        parameterOffset = 12 + (currentParameterIndex * 4)
                        currentParameterIndex += 1
                        self.produce(f"#Parameter is int passed by VAL")
                        self.produce(f"li t0, {x}")
                        self.produce(f"sw t0, -{parameterOffset}(fp)")
                    if (y == "REF"):
                        parameterOffset = 12 + (currentParameterIndex * 4)
                        currentParameterIndex += 1
                        result = self.symbolicTable.search(x)
                        if (result == None):
                            print(f"Terminating Compiler (par1)") 
                            exit(0)
                        (varEntity, scopeOffset) = result
                        if (scopeOffset == 1): #value is in caller func
                            self.produce(f"#Parameter is passed by REF and value is in caller func")
                            self.produce(f"addi t0, sp, -{varEntity.offset}") #t0 now has address of var
                            self.produce(f"sw t0, -{parameterOffset}(fp)") #put address in parameter
                        elif (scopeOffset < self.symbolicTable.getCurrentScope().level): #value is in ancestor of calling func
                            self.produce(f"#Parameter is passed by REF and value is in ancestor of caller func")
                            self.gnlvcode(x)
                            self.produce(f"sw t0, -{parameterOffset}(fp)")
                        elif (scopeOffset == self.symbolicTable.getCurrentScope().level): #value is global
                            self.produce(f"#Parameter is passed by REF and value global")
                            self.produce(f"addi t0, gp, -{varEntity.offset}")
                            self.produce(f"sw t0, -{parameterOffset}(fp)")
                        else:
                            print("Value is in invalid place, terminating")
                    elif (y == "RET"):
                        self.produce(f"#Parameter is return value")
                        returnVar = self.symbolicTable.search(x)
                        if (returnVar == None): 
                            print("Terminating Compiler (par2)") 
                            exit(0)
                        self.produce(f"addi t0, sp, -{returnVar[0].offset}")
                        self.produce("sw t0, -8(fp)")
                elif (op == "call"):
                    #Reset Paramater vars
                    currentParameterIndex = 0
                    isFirstPar = True
                    #get next func entity
                    result = self.symbolicTable.search(x)
                    if (result == None):
                        print("Terminating Compiler (call)") 
                        exit(0)
                    (FuncEntity, _) = result
                    #Store current act graph in next function Act Graph
                    functionBeingCalled = FuncEntity.name
                    
                    if (functionBeingCalled == currentFunction or self.functionsAndTheirLevels[functionBeingCalled] == self.functionsAndTheirLevels[currentFunction]):
                        self.produce(f"#Sibling Func or Recursion")
                        self.produce(f"sw t0, -4(sp)")
                        self.produce(f"sw t0, -4(fp)")
                    else:
                        self.produce(f"#Parent-Child Func")
                        self.produce(f"sw sp, -4(fp)")
                    #get the new framelength
                    frameLength = FuncEntity.framelength
                    #Store current ra in current graph
                    self.produce(f"addi sp, sp, {frameLength}")
                    self.produce(f"jal {x}")
                    self.produce(f"addi sp, sp, -{frameLength}")
                elif (op == "end_block"):
                    self.produce(f"#End of {x}")
                    self.produce("lw ra, 0(sp)")
                    self.produce("jr ra")
                elif (op == "ret"):
                    self.produce(f"#Return {z}")
                    if (z[0] in "0123456789"):
                        self.produce(f"li t1, {z}")
                    else:
                        self.loadVariable(z, "t1")
                        # self.produce(f"lw t1, -{symbolicTable.search(z)[0].offset}(sp)") #load in t1 the value of the return variable
                    self.produce(f"lw t0, -8(sp)") #load in t0 the address of the return variable
                    self.produce(f"sw t1, 0(t0)")#put the return value in the address of the return variable
                elif (op == "in"):
                    self.produce(f"#Input")
                    self.produce("li a7, 5")
                    self.produce("ecall")
                    self.produce(f"#Store input from a0 in {x}")
                    if(self.storeVariable(x, "a0")):
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                elif (op == "out"):
                    self.produce(f"#Print {x}")
                    if(self.loadVariable(x, "a0")):
                        print(f"Variable {x} in function {self.symbolicTable.table.scopes[-2].entities[-1].name} is a global variable but the global keyword wasnt used") 
                        print(f"Line: {line}")
                        exit(0)
                    self.produce("li a7, 1")
                    self.produce("ecall")
                    self.produce("la a0, strNewline")
                    self.produce("li a7, 4")
                    self.produce("ecall")
   