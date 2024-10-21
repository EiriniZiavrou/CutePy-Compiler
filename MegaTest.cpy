#int globalVariableWithALongAssNameThatWillThrowAWarning, bob
##This is supposed to be a file that tests all core aspects that should be fully functional, not 100% exhaustive but close##
def parent(x):#{
   
    def child(y):#{ ##Test Function in a function##
        #int k
        k = child(0) ##Test recursion##
        return y + 1 ##Test return variable/ temporary var##
    #}

    def unwantedChild():#{ ##Test function sibling##
        return child(5)  ## Test return function, also test passing int which gets passed by VAL##
    #}

    global bob ##Test global declarations##
    bob = 1000000000 ##Test very large numbers##
    bob = (x + 1 * (13) // 5 % 3) * 0 ##Test All arithmetic operators##
    bob = unwantedChild() ##Test function call##
    if (13 > 5 and 2 < 14 or 3 == 3): ##Test logical operators##
        bob = 0
    else:
        bob = 0
    return bob
#}

#def main
#int o1, o2
o1 = int(input()) ##Test input##
o2 = o1
o1 = parent(o1) ##Test passing variable which gets passed by REF##
print(o2) ##Test output##