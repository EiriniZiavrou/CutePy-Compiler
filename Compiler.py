from Syntax import Syntax


if __name__ == "__main__":
    print("Enter the file name (Must be in the same folder as this script): ", end = "")
    fileName = input()
    syntax = Syntax(fileName)
    print(f"Starting Syntax/Lectical Analysis on {fileName}")
    syntax.startRule()
    if syntax.getSyntaxHasError(): 
        print("Program Failed!")
        exit(0)
    fileNameWithoutExtension = fileName.split(".")[0]
    print("Program Compiled Succesfully!")
    print(f"The symbol table can be found in {fileNameWithoutExtension}.sym")
    print(f"The intermidiate code can be found in {fileNameWithoutExtension}.int")
    print(f"The final code can be found in {fileNameWithoutExtension}.asm")
