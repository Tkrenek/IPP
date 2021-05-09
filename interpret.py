import sys
import xml.etree.ElementTree as et
import re
import getopt

# Třída pro vypsání nápovědy
class Help():
    def getHelp(self):
        print("Part 2: Interpret")
        print("Param: --source=\"file\" for file with xml")
        print("Param: --input=\"file\" for file with input for interpret")

# Funkce pro zjištění správného počtu operandů
def numberArg(inst):
    if inst in ["MOVE", "INT2CHAR", "READ", "STRLEN", "TYPE", "NOT"]:
        return 2
    elif inst in ["CLEARS", "INT2CHARS", "STRI2INTS",  "ADDS", "SUBS", "MULS",
                  "IDIVS", "LTS", "GTS", "EQS", "ANDS", "ORS", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN",
                  "BREAK"]:
        return 0
    elif inst in ["NOTS", "JUMPIFEQS", "JUMPIFNEQS", "DEFVAR", "CALL", "PUSHS", "POPS", "WRITE", "LABEL", "JUMP", "EXIT", "DPRINT"]:
        return 1
    elif inst in ["ADD", "SUB", "IDIV", "MUL", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "CONCAT", "GETCHAR",
                 "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"]:
        return 3
    else:
       sys.stderr.write("Unknown instruction")
       sys.exit(32)

# seznam pro ověření platnosti instrukce
instrs = ["DEFVAR", "MOVE", "LABEL", "JUMPIFEQ", "WRITE", "CONCAT", "JUMP", "INT2CHAR",
         "READ", "STRLEN", "TYPE", "NOT", "CREATEFRAME", "PUSHFRAME", "POPFRAME",
          "RETURN", "BREAK", "CALL", "PUSHS", "POPS", "EXIT", "DPRINT", "ADD", "SUB",
         "IDIV", "MUL", "LT", "GT", "EQ", "AND", "OR", "STRI2INT", "GETCHAR", "SETCHAR",
        "JUMPIFNEQ", "CLEARS", "ADDS", "SUBS", "MULS", "IDIVS", "LTS", "GTS", "EQS", "ANDS",
        "ORS", "NOTS", "INT2CHARS", "STRI2INTS", "JUMPIFEQS", "JUMPIFNEQS"]

# seznam, které typy může obsahovat symb
symb = ["nil", "bool", "int", "string", "var"]

# slovníky pro rámce a seznam pro zásobník
GF = {}
LF = None
TF = None
data_stack = []
jump_stack = []

pomoc = Help()

# práce s argumenty
argv = sys.argv[1:]
opts = ["source=", "input=", "help"]
oplist, args = getopt.getopt(argv, "s:i:h",opts)

if oplist == []:
    sys.stderr.write("Bad combination of parametres\n")
    sys.exit(10)

# pokud jsou 2 argumenty
if len(argv) == 2:
    for opt in oplist:
        if opt[0] == "--input":
            inp = opt[1]
            try:
                sys.stdin = open(inp, "r")
            except FileNotFoundError:
                sys.stderr.write("Problem with file\n")
                sys.exit(11)
        elif opt[0] == "--source":
            sour = opt[1]
            try:
                file = open(sour, "r")
            except FileNotFoundError:
                sys.stderr.write("Problem with file\n")
                sys.exit(11)
        else:
            sys.stderr.write("Bad combination of parametres\n")
            sys.exit(10)
# pokud je 1 argument
elif len(argv) == 1:
    for opt in oplist:
        if opt[0] == "--input":
            inp = opt[1]
            file = sys.stdin.readlines()
            try:
                sys.stdin = open(inp, "r")
            except FileNotFoundError:
                sys.stderr.write("Problem with file\n")
                sys.exit(11)
            
        elif opt[0] == "--source":
            sour = opt[1]
            try:
                file = open(sour, "r")
            except FileNotFoundError:
                sys.stderr.write("Problem with file\n")
                sys.exit(11)
        elif opt[0] == "--help":
            pomoc.getHelp()
            sys.exit(0)
        else:
            sys.stderr.write("Bad combination of parametres\n")
            sys.exit(10)

else:
    sys.stderr.write("Bad combination of parametres\n")
    sys.exit(10)

# funkce pro uložení typu a hodnoty do proměnné
def putToVar(var, actual):
    typ, val = var.split("@", 1)
    if typ == "GF":
        GF[val][0] = actual[0]
        GF[val][1] = actual[1]
    if typ == "TF":
        TF[val][0] = actual[0]
        TF[val][1] = actual[1]
    if typ == "LF":
        LF[-1][val][0] = actual[0]
        LF[-1][val][1] = actual[1]

# funkce pro ověření zda je proměná inicializována
def isInicialized(var):
    typ, val = var.split("@", 1)
    if typ == "GF":
        if val in GF:
            return True
    elif typ == "TF":
        if TF == None:
            sys.stderr.write("TF not defined\n")
            sys.exit(55)
        if val in TF:
            return True
    elif typ == "LF":
        if LF == None:
            sys.stderr.write("LF not defined\n")
            sys.exit(55)
        try:
            if val in LF[-1]:
               return True    
        except IndexError:
            sys.stderr.write("Problem with LF\n")
            sys.exit(55)

# funkce pro ověření zda je proměná deklarována            
def isDeclared(var):
    typ, val = var.split("@", 1)
    if typ == "GF":
        if GF[val][0] != None:
            return True
    elif typ == "TF":
        if TF[val][0] != None:
            return True
    elif typ == "LF":
        if LF[-1][val][0] != None:
            return True  

# funkce pro nahrazení escape sekvencí    
def replace_esc_seq(string):
    if string == "":
        return string
    pattern = re.compile(r'(\\[0-9]{3})')
    substrings = pattern.split(string)
    string = ""
    #print(substrings)
    for substring in substrings:
        if pattern.match(substring):
            substring2 = substring.split("\\", 1)
            substring = chr(int(substring2[1]))
        string = string + substring
    return string

#Funkce pro instrukci DEFVAR
def defVar(var):
    typ, name = var.split("@", 1)
    if typ == "GF":
        if name in GF:
            sys.stderr.write("Var is already in GF\n")
            sys.exit(52)
        GF[name] = [None, None]
    elif typ == "LF":
        if LF == [] or LF ==  None:
            sys.stderr.write("LF doesnt exist\n")
            sys.exit(55)
        if name in LF[-1]:
            sys.stderr.write("Var is already in LF\n")
            sys.exit(52)
        LF[-1][name] = [None, None]
    elif typ == "TF":
        if TF == None:
            sys.stderr.write("TF doesnt exist\n")
            sys.exit(55)
        if name in TF:
            sys.stderr.write("Var is already in TF\n")
            sys.exit(52)
        TF[name] = [None, None]
 
#Funkce pro získání hodnoty z proměnné
def getValFromVar(symb):
    if isInicialized(symb) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if isDeclared(symb) != True:
        sys.stderr.write("Var is not initialized\n")
        sys.exit(56)
    typ, val = symb.split("@", 1)
    if typ == "GF":
        type = GF[val][0]
        value = GF[val][1]
    elif typ == "TF":
            type = TF[val][0]
            value = TF[val][1]
    elif typ == "LF":
            type = LF[-1][val][0]
            value = LF[-1][val][1]
    return type, value

#funkce pro instrukci MOVE
def move(var, symb, type):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if type == "var": # přiřazujeme proměnnou
        typ, value = var.split("@", 1)
        datatype, value1 = getValFromVar(symb)
        
        if typ == "GF":
            GF[value] = [datatype, value1]
        elif typ == "LF":
            LF[-1][value] = [datatype, value1]
        elif typ == "TF":
            TF[value] = [datatype, value1]
    else: # přiřazujeme konstantu
        typ, value = var.split("@", 1)
        if type == "string" and symb == None:
            symb = ""
        if typ == "GF":
            GF[value] = [type, symb]
        elif typ == "LF":
            LF[-1][value] = [type, symb]
        elif typ == "TF":
            TF[value] = [type, symb]

# funkce pro push do zásobníku
def pushs(symb, type):
    if type == "var":
        typ, val = getValFromVar(symb)
        data_stack.append([typ, val])
    else:
        data_stack.append([type, symb])

# funkce pro pop ze zásobníku
def pops(var):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if data_stack == []:
        sys.stderr.write("Stack is empty\n")
        sys.exit(56)
    
    actual = data_stack.pop()
    putToVar(var, actual)

# funkce pro matematické operace
def math_oper(var, symb1, symb2, typ1, typ2, operace):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "int":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
    elif typ2 == "int":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 != "int" or typ2 != "int":
        sys.stderr.write("Operand is not int\n")
        sys.exit(53)
    if operace == "add":
        vysl = int(symb11) + int(symb22)
    elif operace == "sub":
        vysl = int(symb11) - int(symb22)
    elif operace == "mul":
        vysl = int(symb11) * int(symb22)
    elif operace == "div":
        try:
            vysl = int(symb11) // int(symb22)
        except ZeroDivisionError:
            sys.stderr.write("Can´t to div by zero\n")
            sys.exit(57)
    vysl = ["int", str(vysl)]
    putToVar(var, vysl)

# funkce pro relační operace
def rel_oper(var, symb1, symb2, typ1, typ2, operace):
    itIsInt = 0
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    else:
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
    else:
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 != typ2 and typ1 != "nil" and typ2 != "nil":
        sys.stderr.write("Operands doesnt have same type\n")
        sys.exit(53)
    if operace != "eq":
        if typ1 == "nil" or typ2 == "nil":
            sys.stderr.write("Operands doesnt have same type\n")
            sys.exit(53)
    if typ1 == "int" and typ2 == "int":
        itIsInt = 1
    if typ1 == "string":
        symb11 = replace_esc_seq(symb11)
    if typ2 == "string":
        symb22 = replace_esc_seq(symb22)
    vysl = "false"
    if itIsInt == 0:
        if operace == "lt":
            if(symb11 < symb22):
                vysl = "true"
        elif operace == "gt":
            if(symb11 > symb22):
                vysl = "true"
        elif operace == "eq":
            if(symb11 == symb22):
                vysl = "true"
    elif itIsInt == 1:
        if operace == "lt":
            if(int(symb11) < int(symb22)):
                vysl = "true"
        elif operace == "gt":
            if(int(symb11) > int(symb22)):
                vysl = "true"
        elif operace == "eq":
            if(symb11 == symb22):
                vysl = "true"
    vysl = ["bool", vysl]
    putToVar(var, vysl)

# funkce pro logické operace
def bool_oper(var, symb1, typ1, operace, symb2, typ2):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "bool":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
    elif typ2 == "bool":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 != "bool" or typ2 != "bool":
        sys.stderr.write("Operand is not bool\n")
        sys.exit(53)
    vysl = "false"
    if operace == "and":
        if symb11 == "true" and symb22 == "true":
            vysl = "true"
    elif operace == "or":
        if symb11 == "true" or symb22 == "true":
            vysl = "true"
    elif operace == "not":
        if symb11 == "true":
            vysl = "false"
        elif symb11 == "false":
            vysl = "true"
    vysl = ["bool", vysl]
    putToVar(var, vysl)

# funkce pro not
def bool_oper_not(var, symb1, typ1):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "bool":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ1 != "bool":
        sys.stderr.write("Operand is not bool\n")
        sys.exit(53)
    vysl = "false"
    if symb11 == "true":
        vysl = "false"
    elif symb11 == "false":
        vysl = "true"
    vysl = ["bool", vysl]
    putToVar(var, vysl)

# funkce pro instrukci INT2CHAR
def int_to_char(var, symb1, typ1):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "int":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ1 != "int":
        sys.stderr.write("Operand is not int\n")
        sys.exit(53)
    try:
        znak = chr(int(symb11))
    except ValueError:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    vysl = ["string", znak]
    putToVar(var, vysl)

# funkce pro instrukci STRI2INT
def stri_to_int(var, symb1, symb2, typ1, typ2):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "string":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
    elif typ2 == "int":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 != "string" or typ2 != "int":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
    symb11 = replace_esc_seq(symb11)
    if int(symb22) < 0:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    try:
        znak = symb11[int(symb22)]
    except IndexError:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    cislo = ord(znak)
    vysl = ["int", cislo]
    putToVar(var, vysl)

# funkce pro instrukci CONCAT
def concat(var, symb1, symb2, typ1, typ2):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "string":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)

        symb22 = symb2
    elif typ2 == "string":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 != "string" or typ2 != "string":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
    symb22 = replace_esc_seq(symb22)
    symb11 = replace_esc_seq(symb11)
    
    retez = symb11 + symb22
    vysl = ["string", retez]
    putToVar(var, vysl)

# funkce pro instrukci STRLEN
def str_len(var, symb1, typ1):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "string":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ1 != "string":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
    symb11 = replace_esc_seq(symb11)
    delka = len(symb11)
    vysl = ["int", delka]
    putToVar(var, vysl)

# funkce pro instrukci GETCHAR
def getchar(var, symb1, symb2, typ1, typ2):
     if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
     if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
     elif typ1 == "string":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
     if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
     elif typ2 == "int":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
     if typ1 != "string" or typ2 != "int":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
     symb11 = replace_esc_seq(symb11)  
     if int(symb22) < 0:
         sys.stderr.write("Out of index\n")
         sys.exit(58)
     try:
        znak = symb11[int(symb22)]
     except IndexError:
         sys.stderr.write("Out of index\n")
         sys.exit(58)

     vysl = ["string", znak]
     putToVar(var, vysl)

# funkce pro instrukci TYPE
def type_of(var, symb1, typ1):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)

    if typ1 == "var":
        if isInicialized(symb1) != True:
            sys.stderr.write("Var is not defined\n")
            sys.exit(54)
        if isDeclared(symb1) != True:
            typ1 = ""
        else:
            typ, val = symb1.split("@", 1)
        

            if typ == "GF":
                typ1 = GF[val][0]
            elif typ == "TF":
                typ1 = TF[val][0]

            elif typ == "LF":
                typ1 = LF[-1][val][0]

    vysl = ["string", typ1]
    putToVar(var, vysl)

# funkce pro instrukci SETCHAR
def setchar(var, symb1, symb2, typ1, typ2):
     if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
     typVar, symbVar = getValFromVar(var)
     if typVar != "string":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
     if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
     elif typ1 == "int":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
     if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
     elif typ2 == "string":
        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
     if typ1 != "int" or typ2 != "string":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
     symb22 = replace_esc_seq(symb22)
     seznam = list(symbVar)
     if int(symb11) < 0:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
     try:
        seznam[int(symb11)] = symb22[0]
     except IndexError:
         sys.stderr.write("Out of index\n")
         sys.exit(58)
     symbVar = "".join(seznam)
     vysl = ["string", symbVar]
     putToVar(var, vysl)


# funkce pro instrukci WRITE
def write_it_down(symb1, typ1):
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    symb11 = symb1
    if typ1 == "string":
         symb11 = replace_esc_seq(symb11)
    elif typ1 == "nil":
         symb11 = ""
    print(symb11, end='')

# funkce pro instrukci JUMPIFEQ a JUMPIFNEQ
def jumpif(label, symb1, symb2, typ1, typ2, counter, operace):
    
    if label not in labels:
        sys.stderr.write("Label doesnt exist\n")
        sys.exit(52)
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    else:
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ2 == "var":
        typ2, symb2 = getValFromVar(symb2)
        symb22 = symb2
    else:

        symb2 = symb2.split("@", 1)
        symb22 = symb2[0]
    if typ1 == "nil" or typ2 == "nil":
        pass
    else:
        if typ1 != typ2:
            sys.stderr.write("Operands doesnt have same type\n")
            sys.exit(53)

    if typ1 == "string":
        symb11 = replace_esc_seq(symb11)
    if typ2 == "string":
        symb22 = replace_esc_seq(symb22)
    if operace == "eq":
        if symb11 == symb22:
            counter = labels[label]
        else:
            counter = counter
    elif operace == "neq":
        if symb11 != symb22:
            counter = labels[label]
        else:
            counter = counter
    return counter

# funkce pro instrukci EXIT
def myExit(symb1, typ1):
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    elif typ1 == "int":
        symb1 = symb1.split("@", 1)
        symb11 = symb1[0]
    if typ1 != "int":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
    if int(symb11) < 50 and int(symb11) >=0:

        exit(int(symb11))
    else:
        exit(57)

# funkce pro instrukci READ    
def myRead(var, typ):
    if isInicialized(var) != True:
        sys.stderr.write("Var is not defined\n")
        sys.exit(54)
    try:
        hodnota = input()
    except EOFError:
        hodnota = "nil"
        typ = "nil"
    if typ == "int":
        if re.search(r"^[+-]?[0-9]+$", hodnota) is None:
            hodnota = "nil"
            typ = "nil"
    if typ == "bool":
        if hodnota.lower() == "true":
            hodnota = "true"
        else:
            hodnota = "false"
            typ = "bool"
    vysl = [typ, hodnota]
    putToVar(var, vysl)

# funkce pro instrukci DPRINT
def dprint(symb1, typ1):
    if typ1 == "var":
        typ1, symb1 = getValFromVar(symb1)
        symb11 = symb1
    symb11 = symb1
    if typ1 == "string":
         symb11 = replace_esc_seq(symb11)
    elif typ1 == "nil":
         symb11 = ""
    sys.stderr.write(symb11+"\n")

##### FUNKCE PRO INSTRUKCE SE ZÁSOBNÍKEM ####
# funkce pro matematické operace
def stack_maths(operace):    
    try:
        var2 = data_stack.pop()
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    typ2 = var2[0]
    symb1 = var1[1]
    symb2 = var2[1]
    if typ1 != "int" or typ2 != "int":
        sys.stderr.write("Operand is not int\n")
        sys.exit(53)
    if operace == "add":
        vysl = int(symb1) + int(symb2)
    elif operace == "sub":
        vysl = int(symb1) - int(symb2)
    elif operace == "mul":
        vysl = int(symb1) * int(symb2)
    elif operace == "div":
        try:
            vysl = int(symb1) // int(symb2)
        except ZeroDivisionError:
            sys.stderr.write("Can´t to div by zero\n")
            sys.exit(57)
    vysl = ["int", str(vysl)]
    data_stack.append(vysl)

# funkce pro relační operace
def stack_rel(operace): 
    itIsInt = 0
    try:
        var2 = data_stack.pop()
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    typ2 = var2[0]
    symb1 = var1[1]
    symb2 = var2[1]
    if typ1 != typ2 and typ1 != "nil" and typ2 != "nil":
        sys.stderr.write("Operands doesnt have same type\n")
        sys.exit(53)
    if typ1 == "int" and typ2 == "int":
        itIsInt = 1
    if operace != "eq":
        if typ1 == "nil" or typ2 == "nil":
            sys.stderr.write("Operands doesnt have same type\n")
            sys.exit(53)
    if typ1 == "string":
        symb1 = replace_esc_seq(symb1)
    if typ2 == "string":
        symb2 = replace_esc_seq(symb2)
    vysl = "false"
    if itIsInt == 1:
        if operace == "lt":
            if(int(symb1) < int(symb2)):
                vysl = "true"
        elif operace == "gt":
            if(int(symb1) > int(symb2)):
                vysl = "true"
        elif operace == "eq":
            if(int(symb1) == int(symb2)):
                vysl = "true"
    else:
        if operace == "lt":
            if(symb1 < symb2):
                vysl = "true"
        elif operace == "gt":
            if(symb1 > symb2):
                vysl = "true"
        elif operace == "eq":
            if(symb1 == symb2):
                vysl = "true"
    vysl = ["bool", vysl]
    data_stack.append(vysl)

# funkce pro logické operace
def stack_bool(operace):
    try:
        var2 = data_stack.pop()
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    typ2 = var2[0]
    symb1 = var1[1]
    symb2 = var2[1]
    if typ1 != "bool" or typ2 != "bool":
        sys.stderr.write("Operand is not bool\n")
        sys.exit(53)
    vysl = "false"
    if operace == "and":
        if symb1 == "true" and symb2 == "true":
            vysl = "true"
    elif operace == "or":
        if symb1 == "true" or symb2 == "true":
            vysl = "true"
    vysl = ["bool", vysl]
    data_stack.append(vysl)

# funkce pro instrukci NOT
def stack_bool_not():
    try:
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    symb1 = var1[1]

    if typ1 != "bool":
        sys.stderr.write("Operand is not bool\n")
        sys.exit(53)
    vysl = "false"
    if symb1 == "true":
        vysl = "false"
    elif symb1 == "false":
        vysl = "true"
    vysl = ["bool", vysl]
    data_stack.append(vysl)

# funkce pro instrukci INT2CHARS
def intToChars():
    try:
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    symb1 = var1[1]
    if typ1 != "int":
        sys.stderr.write("Operand is not int\n")
        sys.exit(53)
    try:
        znak = chr(int(symb1))
    except ValueError:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    vysl = ["string", znak]
    data_stack.append(vysl)

# funkce pro instrukci STRI2INT
def striToInts():
    try:
        var2 = data_stack.pop()
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    typ2 = var2[0]
    symb1 = var1[1]
    symb2 = var2[1]
    if typ1 != "string" or typ2 != "int":
        sys.stderr.write("Bad type of operand\n")
        sys.exit(53)
    symb1 = replace_esc_seq(symb1)
    if int(symb2) < 0:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    try:
        znak = symb1[int(symb2)]
    except IndexError:
        sys.stderr.write("Out of index\n")
        sys.exit(58)
    cislo = ord(znak)
    vysl = ["int", cislo]
    data_stack.append(vysl)

# funkce pro JUMPIFEQS a JUMPIFNEQS
def jumpIfEqs(operace, label, counter):
    try:
        var2 = data_stack.pop()
        var1 = data_stack.pop()
    except IndexError:
        sys.stderr.write("Stack is empty\n")
        exit(58)
    typ1 = var1[0]
    typ2 = var2[0]
    symb1 = var1[1]
    symb2 = var2[1]
    if typ1 == "nil" or typ2 == "nil":
        pass
    else:
        if typ1 != typ2:
            sys.stderr.write("Operands doesnt have same type\n")
            sys.exit(53)
    if typ1 == "string":
        symb1 = replace_esc_seq(symb1)
    if typ2 == "string":
        symb2 = replace_esc_seq(symb2)
    if operace == "eq":
        if symb1 == symb2:
            counter = labels[label]
        else:
            counter = counter
    elif operace == "neq":
        if symb1 != symb2:
            counter = labels[label]
        else:
            counter = counter
    return counter

# čtení ze vstupního souboru xml
text = ""
for line in file:
    text = text + line

try:
    program = et.fromstring(text)
except:
    sys.stderr.write("bad xml\n")
    sys.exit(31)
    
special = []
i = 0
if program.attrib["language"] != "IPPcode20":
    sys.stderr.write("Language must be IPPCODE20\n")
    sys.exit(32)

toWrite = []
instrInFile = {}
arguments = {}
types = {}
labels = {}
counter = 0

#  lexikální a syntaktická kontrola
for inst1 in program:
    numberOfArg = len(inst1)

    if numberOfArg == 0:
        continue

    if numberOfArg == 1:
        if inst1[0].tag not in ["arg1"]:
            sys.stderr.write("Bad argument tag\n")
            sys.exit(32)
    elif numberOfArg == 2:
        if inst1[0].tag == inst1[1].tag:
            sys.stderr.write("Duplicit arg\n")
            sys.exit(32)
        if inst1[0].tag not in ["arg1", "arg2"] or inst1[1].tag not in ["arg1", "arg2"]:
            sys.stderr.write("Bad argument tag\n")
            sys.exit(32)
    elif numberOfArg == 3:
        if inst1[0].tag == inst1[1].tag or inst1[0].tag == inst1[2].tag or inst1[1].tag == inst1[2].tag:
            sys.stderr.write("Duplicit arg\n")
            sys.exit(32)
        if inst1[0].tag not in ["arg1", "arg2", "arg3"] or inst1[1].tag not in ["arg1", "arg2", "arg3"] or inst1[2].tag not in ["arg1", "arg2", "arg3"]:
            sys.stderr.write("Bad argument tag\n")
            sys.exit(32)
    i = 0
    #lexikální kontrola
    while i < numberOfArg:
        if "type" not in inst1[i].attrib:
            sys.stderr.write("Missing some attribute in xml\n")
            sys.exit(32)
        if re.search(r"^arg\d$", inst1[i].tag) is None:
            sys.stderr.write("Missing some attribute in xml\n")
            sys.exit(32)
        
        if inst1[i].attrib["type"] == "int":
            if re.search(r"^[+-]?[0-9]+$", inst1[i].text) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        elif inst1[i].attrib["type"] == "bool":
            if re.search(r"^(true|false)$", inst1[i].text) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        elif inst1[i].attrib["type"] == "nil":
            if re.search(r"^nil$", inst1[i].text) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        elif inst1[i].attrib["type"] == "string" and inst1[i].text != "":
            if re.search(r"^(\\[0-9]{3}|[^\\])*$", str(inst1[i].text)) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        elif inst1[i].attrib["type"] == "var":
            if re.search(r"^(LF|TF|GF)@[A-Za-z_\-&\?!%$*][A-Za-z0-9_\-&\?!%$*]*$", inst1[i].text) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        elif inst1[i].attrib["type"] == "label":
            if re.search(r"^[a-zA-Z_\-&\?!%$*][a-zA-Z0-9_\-&\?!%$*]*$", inst1[i].text) is None:
                sys.stderr.write("Bad xml\n")
                sys.exit(32)
        i += 1
orders = [0]
# Načítání xml
for inst in program:
    if "order" not in inst.attrib or "opcode" not in inst.attrib:
        sys.stderr.write("Missing some attribute in xml\n")
        sys.exit(32)
    try:
        if int(inst.attrib["order"]) in orders:
            sys.stderr.write("Order was used\n")
            sys.exit(32)
    except ValueError:
        sys.stderr.write("Order cant be string\n")
        sys.exit(32)
    orders.append(int(inst.attrib["order"]))
    if int(inst.attrib["order"]) < max(orders):
        sys.stderr.write("Missing some attribute in xml\n")
        sys.exit(32)
    
    if inst.tag != "instruction":
        sys.stderr.write("Bad name of tag\n")
        sys.exit(32)
    if int(inst.attrib["order"]) <= 0:
        sys.stderr.write("Order is zero or under\n")
        sys.exit(32)
    inst.attrib["opcode"] = inst.attrib["opcode"].upper()
    if (inst.attrib["opcode"]) in instrs:
        instrInFile[counter] = inst.attrib["opcode"]          
        if inst.attrib["opcode"] == "LABEL":
            if inst[0].text in labels:
                sys.stderr.write("Label exists\n")
                sys.exit(52)
            labels[inst[0].text] = counter
        numArg = len(inst)

        if numArg == 0:
            arguments[counter] = [""]
            types[counter] = [""]
        elif numArg == 1:

            if inst[0].attrib["type"] == "string" and inst[0].text == None:
                inst[0].text = ""
            arguments[counter] = [inst[0].text]
            types[counter] = [inst[0].attrib["type"]]
        elif numArg == 2:
            if inst[0].attrib["type"] == "string" and inst[0].text == None:
                inst[0].text = ""
            if inst[1].attrib["type"] == "string" and inst[1].text == None:
                inst[1].text = ""
            arguments[counter] = [inst[0].text, inst[1].text]
            types[counter] = [inst[0].attrib["type"], inst[1].attrib["type"]]
        else:
            if inst[0].attrib["type"] == "string" and inst[0].text == None:
                inst[0].text = ""
            if inst[1].attrib["type"] == "string" and inst[1].text == None:
                inst[1].text = ""
            if inst[2].attrib["type"] == "string" and inst[2].text == None:
                inst[2].text = ""
            arguments[counter] = [inst[0].text, inst[1].text, inst[2].text]
            types[counter] = [inst[0].attrib["type"], inst[1].attrib["type"], inst[2].attrib["type"]]
        counter += 1      
        
        for arg in inst:
            if len(inst) != numberArg(inst.attrib["opcode"]):
                sys.stderr.write("Bad count of operands in xml\n")
                sys.exit(32)
    else:
        sys.stderr.write("Unknown instruction\n")
        sys.exit(32)



# Procházení ve slovníku s instrukcemi a provádění instrukcí a kontrola správného typu operandů
counter2 = counter
counter = 0
while counter < counter2:
    if instrInFile[counter] == "DEFVAR":
        if(types[counter][0] != "var"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        defVar(arguments[counter][0])
    elif instrInFile[counter] == "MOVE":
        if(types[counter][0] != "var" or types[counter][1] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        move(arguments[counter][0], arguments[counter][1], types[counter][1])
    elif instrInFile[counter] == "CREATEFRAME":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        TF = {}
    elif instrInFile[counter] == "PUSHFRAME":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        if TF == None:
            sys.stderr.write("TF doesnt exists\n")
            sys.exit(55)
        if LF == None:
            LF = []
        LF.append(TF)
        TF = None
    elif instrInFile[counter] == "POPFRAME":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        if LF == [] or LF == None:
            sys.stderr.write("Stack of frames is empty\n")
            sys.exit(55)
        TF = LF.pop()
    elif instrInFile[counter] == "CALL":
        if(types[counter][0] != "label"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        if arguments[counter][0] not in labels:
            sys.stderr.write("Label doesnt exists\n")  
            sys.exit(52)
        counterjump = counter
        jump_stack.append(counterjump)
        counter = labels[arguments[counter][0]]
    elif instrInFile[counter] == "RETURN":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        if jump_stack == []:
            sys.stderr.write("No call\n")  
            sys.exit(56)
        counter = jump_stack.pop() 
    elif instrInFile[counter] == "PUSHS":
        if(types[counter][0] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        pushs(arguments[counter][0], types[counter][0])     
    elif instrInFile[counter] == "POPS":
        if(types[counter][0] != "var"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        pops(arguments[counter][0])    
    elif instrInFile[counter] == "ADD":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        math_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "add")
    elif instrInFile[counter] == "SUB":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        math_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "sub")
    elif instrInFile[counter] == "MUL":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        math_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "mul")
    elif instrInFile[counter] == "IDIV":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        math_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "div")
    elif instrInFile[counter] == "LT":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        rel_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "lt")
    elif instrInFile[counter] == "GT":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xmlv")
            sys.exit(32)
        rel_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "gt")
    elif instrInFile[counter] == "EQ":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xmlv")
            sys.exit(32)
        rel_oper(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], "eq")
    elif instrInFile[counter] == "AND":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        bool_oper(arguments[counter][0], arguments[counter][1], types[counter][1], "and", arguments[counter][2], types[counter][2])
    elif instrInFile[counter] == "OR":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        bool_oper(arguments[counter][0], arguments[counter][1], types[counter][1], "or", arguments[counter][2], types[counter][2])
    elif instrInFile[counter] == "NOT":
        if(types[counter][0] != "var" or types[counter][1] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        bool_oper_not(arguments[counter][0], arguments[counter][1], types[counter][1])
    elif instrInFile[counter] == "INT2CHAR":
        if(types[counter][0] != "var" or types[counter][1] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        int_to_char(arguments[counter][0], arguments[counter][1], types[counter][1])
    elif instrInFile[counter] == "STRI2INT":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stri_to_int(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2])
    elif instrInFile[counter] == "READ":
        if(types[counter][0] != "var" or types[counter][1] != "type"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        myRead(arguments[counter][0], arguments[counter][1])
    elif instrInFile[counter] == "WRITE":
        if(types[counter][0] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        write_it_down(arguments[counter][0], types[counter][0]) 
    elif instrInFile[counter] == "CONCAT":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        concat(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2])
    elif instrInFile[counter] == "STRLEN":
        if(types[counter][0] != "var" or types[counter][1] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        str_len(arguments[counter][0], arguments[counter][1], types[counter][1])     
    elif instrInFile[counter] == "GETCHAR":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        getchar(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2])
    elif instrInFile[counter] == "SETCHAR":
        if(types[counter][0] != "var" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        setchar(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2])         
    elif instrInFile[counter] == "TYPE":
        if(types[counter][0] != "var" or types[counter][1] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)         
        type_of(arguments[counter][0], arguments[counter][1], types[counter][1])
    elif instrInFile[counter] == "LABEL":
        if(types[counter][0] != "label"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
    elif instrInFile[counter] == "JUMP":
        if(types[counter][0] != "label"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        if arguments[counter][0] not in labels:
            sys.stderr.write("Label doesnt exists\n")
            sys.exit(52)
        counter = labels[arguments[counter][0]]
    elif instrInFile[counter] == "JUMPIFEQ":
        if(types[counter][0] != "label" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        counter = jumpif(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], counter, "eq")
    elif instrInFile[counter] == "JUMPIFNEQ":
        if(types[counter][0] != "label" or types[counter][1] not in symb or types[counter][2] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        counter = jumpif(arguments[counter][0], arguments[counter][1], arguments[counter][2], types[counter][1], types[counter][2], counter, "neq")
    elif instrInFile[counter] == "EXIT":
        if(types[counter][0] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        myExit(arguments[counter][0], types[counter][0])
    elif instrInFile[counter] == "DPRINT":
        if(types[counter][0] not in symb):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        dprint(arguments[counter][0], types[counter][0])
    elif instrInFile[counter] == "BREAK":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
    elif instrInFile[counter] == "CLEARS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        data_stack = []
    elif instrInFile[counter] == "ADDS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_maths("add")
    elif instrInFile[counter] == "SUBS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_maths("sub")
    elif instrInFile[counter] == "MULS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_maths("mul")
    elif instrInFile[counter] == "IDIVS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)    
        stack_maths("div")
        
    elif instrInFile[counter] == "LTS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_rel("lt")
    elif instrInFile[counter] == "GTS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_rel("gt")
    elif instrInFile[counter] == "EQS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)    
        stack_rel("eq")
    elif instrInFile[counter] == "ANDS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_bool("and")
    elif instrInFile[counter] == "ORS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_bool("or")
    elif instrInFile[counter] == "NOTS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        stack_bool_not()
    elif instrInFile[counter] == "INT2CHARS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        intToChars()
    elif instrInFile[counter] == "STRI2INTS":
        if(types[counter][0] != ""):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        striToInts()
    elif instrInFile[counter] == "JUMPIFEQS":
        if(types[counter][0] != "label"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        counter = jumpIfEqs("eq", arguments[counter][0], counter)
    elif instrInFile[counter] == "JUMPIFNEQS":
        if(types[counter][0] != "label"):
            sys.stderr.write("Bad type of operand in xml\n")
            sys.exit(32)
        counter = jumpIfEqs("neq", arguments[counter][0], counter)

    counter += 1

