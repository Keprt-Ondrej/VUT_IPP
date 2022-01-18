#!/usr/bin/env python3

#autor: xkeprt03, Ondřej Keprt

from interpret_functions import frame
from interpret_functions import get_argument
import argparse
import sys
from xml.etree import ElementTree as ET
import re
from collections import OrderedDict

#definice globálních proměnných
instr_max_order = 0 #sem se doplni nejvyssi hodnota z poradi operaci
local_frames = []
labels = {}
GF = frame()
TF = None       #createframe sem prilepi a objekt frame() a dale se s nim pracuje podobne jako s GF
stack = []
call_stack = []
instruction_arr = OrderedDict()

# definice funkcí a tříd jednotlivých instrukcí
# pro začátek vykonávání programu vyhledejte: #main 

def log_inside():
    #debugovani a je vyuzita pro instrukci break
    global TF,GF,local_frames,labels,call_stack,stack,instr_walker    
    print("---------------------------------------------------------------",file=sys.stderr)
    print("GF:",vars(GF),file=sys.stderr)
    if TF != None:    
        print("TF:",vars(TF),file=sys.stderr)
    else:
        print("TF je None",file=sys.stderr)

    if not local_frames:
        print("Neni lokalni frame",file=sys.stderr)
    else:
        print("LF top:",vars(local_frames[-1]),file=sys.stderr) 

    print("Labels:",labels,file=sys.stderr)
    print("call stack:",call_stack,file=sys.stderr)
    print("stack:",stack,file=sys.stderr)
    print("instrukce:",instr_walker,file=sys.stderr)
    print("---------------------------------------------------------------",file=sys.stderr)

def string_repair(my_str):
    #odstraneni escape sekvenci z retezce
    #vraci opraveny retezec
    if (my_str == None):
        return ""

    find = re.findall("\\\\[0-9][0-9][0-9]",my_str)
    for substring in find:
        my_str = my_str.replace(substring,chr(int(substring.replace("\\",""))))
    return my_str
   
def def_var(var):
    #definovani promenne v ramci
    #podle promenne rozhodne, kterej ramec pouzijeme
    #vola metody daneho ramce, ktery promennou definuji
    global TF
    global GF
    global local_frames
    defining = var.split('@')
    if defining[0] == "GF":
        GF.def_var_frame(defining[1])
    elif defining[0] == "TF":
        if TF != None:
            TF.def_var_frame(defining[1])
        else:
            print("Pristup k neexistujicimu ramci: ",defining[0],file=sys.stderr)
            exit(55) 
    else:
        if not local_frames:
            print("Pristup k neexistujicimu ramci: ",defining[0],file=sys.stderr)
            exit(55) 
        else:
            local_frames[-1].def_var_frame(defining[1])

def get_var(var):
    #vraci typ promenne a hodnotu promenne 
    #podle promenne rozhodne, kterej ramec pouzijeme
    #vola metody daneho ramce, ktery promennou vrati
    global TF
    global GF
    global local_frames
    from_var = var.split('@')
    if from_var[0] == "GF":
        return GF.get_var_frame(from_var[1])
    elif from_var[0] == "TF":
        if TF != None:
            return TF.get_var_frame(from_var[1])
        else:
            print("Pristup k neexistujicimu ramci: ",from_var[0],file=sys.stderr)
            exit(55) 
    else:
        if not local_frames:
            print("Pristup k neexistujicimu ramci: ",from_var[0],file=sys.stderr)
            exit(55) 
        else:
            return local_frames[-1].get_var_frame(from_var[1])    

def set_var(var_name,new_type,new_value):
    #nastavuje typ a hodnotu promenne
    #podle promenne rozhodne, kterej ramec pouzijeme
    #vola metody daneho ramce, ktery promennou nastavi
    global TF
    global GF
    global local_frames
    if new_type == "string":        
        new_value = string_repair(new_value)

    seting = var_name.split('@')
    if seting[0] == "GF":
        GF.set_var_frame(seting[1],new_value,new_type)
    elif seting[0] == "TF":
        if TF != None:
            TF.set_var_frame(seting[1],new_value,new_type)
        else:
            print("Pristup k neexistujicimu ramci: ",seting[0],file=sys.stderr)
            exit(55) 
    else:
        if not local_frames:
            print("Pristup k neexistujicimu ramci: ",seting[0],file=sys.stderr)
            exit(55) 
        else:
            local_frames[-1].set_var_frame(seting[1],new_value,new_type)        

def move_var(desination_var,symb_type,symb_value):
    #nastavuje typ a hodnotu promenne, kterou precte z promenne predane pomoci symb_value 
    #nebo nastavi prislusnou konstantu
    #podle promenne rozhodne, kterej ramec pouzijeme
    #vola metody daneho ramce, ktery promennou nastavi
    global TF
    global GF
    global local_frames
    new_type = None
    new_value = None    
    if symb_type == "var":    
        new_type, new_value = get_var(symb_value)
    else:
        new_type = symb_type
        new_value = symb_value   

    set_var(desination_var,new_type,new_value)

def str_to_bool(string):
    #v pameti je vse ulozeno jako string, proto potrebuji funkci na prevod
    if string == "true":
        return True
    else:
        return False

def bool_to_str(bool_val):
    #v pameti je vse ulozeno jako string, proto potrebuji funkci na prevod
    if bool_val:
        return "true"
    else:
        return "false"

class instruction:
    def __init__(self,xml_instr): 
        print("spatny OPCODE instrukce",file=sys.stderr)
        exit(32)

    def find_max_order(self,order):
        #meni zarazku, ktera slouzi pro pruchod polem instrukci
        global instr_max_order             
        if instr_max_order < order:
            instr_max_order = order 

    def store_instruction(self,order):
        # prida do pole instrukci dany objekt instrukce
        # kontroluje, zda nemame vice funkci se stejnym order         
        self.find_max_order(order)
        if order in instruction_arr:
            print("Instrukce s poradim ",order," se vyskytuje vice nez 1x",file=sys.stderr)
            exit(32) 
        else:
            instruction_arr[order] = self

    def run_instruction(self):
        #funkce, ktera provede instrukci
        pass   
    
    def print_self(self):
        #funkce pro debug
        print("I am instruction: ",self,"\t",vars(self),file=sys.stderr)

#tridy pro jednotlive instrukce
#kazda ma definovanuy pouze konstruktor a funkci pro provedeni instrukce
class IPP_move(instruction): 
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")                 
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        move_var(self.arg1_value,self.arg2_type,self.arg2_value)

class IPP_createframe(instruction):
    def __init__(self,xml_instr):                
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):        
        global TF        
        TF = frame()

class IPP_pushframe(instruction):
    def __init__(self,xml_instr):        
        self.store_instruction(int(xml_instr.attrib["order"])) 
        
    def run_instruction(self):
        global TF
        global local_frames
        if TF != None:
            local_frames.append(TF)
            TF = None
        else:
            print("Pokus o přístup k nedefinovanému rámci ", file=sys.stderr)
            exit(55)

class IPP_popframe(instruction):
    def __init__(self,xml_instr):        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        global local_frames
        global TF
        if not local_frames:
            print("Nexistujici zadny lokalni ramec", file=sys.stderr)
            exit(55)
        else:
           TF = local_frames[-1]
           local_frames.pop() 
           
class IPP_defvar(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")                        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):        
        def_var(self.arg1_value)          

class IPP_call(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"label")
        self.opcode = int(xml_instr.attrib["order"])         
        self.store_instruction(self.opcode)

    def run_instruction(self):
        global labels
        global instr_walker
        global call_stack
        if self.arg1_value in labels:
            instr_walker = labels[self.arg1_value]
            call_stack.append(self.opcode)
        else:
            print("Label nexistuje: ",self.arg1_value,file=sys.stderr)
            exit(52)
        
class IPP_return(instruction):
    def __init__(self,xml_instr):        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self): 
        global call_stack
        global instr_walker
        if not call_stack:
            print("snazite se dostat hodnotu z prazdneho zasobniku volani funkci",file=sys.stderr)
            exit(56)
        else:
            instr_walker = call_stack[-1]
            call_stack.pop()        

class IPP_pushs(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"symb")       
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        pushed_type = None
        pushed_value = None
        if self.arg1_type == "var":
            pushed_type,pushed_value = get_var(self.arg1_value)
        else:
            pushed_type = self.arg1_type
            pushed_value = self.arg1_value       
        stack.append([pushed_type,pushed_value])

class IPP_pops(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        global stack
        if not stack:
            print("snazite se dostat hodnotu z prazdneho zasobniku",file=sys.stderr)
            exit(56)
        else:
            new = stack[-1]
            stack.pop()
            set_var(self.arg1_value,new[0],new[1])

class IPP_add(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")         
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) + int(operand_2_value)
            set_var(self.arg1_value,"int",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_sub(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")         
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) - int(operand_2_value)
            set_var(self.arg1_value,"int",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_mul(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) * int(operand_2_value)
            set_var(self.arg1_value,"int",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_idiv(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")          
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            if int(operand_2_value) == 0:
                print("Nelze delit nulou",file=sys.stderr)
                exit(57)
            else:
                result = int(operand_1_value) // int(operand_2_value)
                set_var(self.arg1_value,"int",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_LT(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) < int(operand_2_value)
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        elif operand_1_type == "bool" and operand_2_type == "bool":
            if operand_1_value == "false" and operand_2_value == "true":
                set_var(self.arg1_value,"bool","true")
            else:
                set_var(self.arg1_value,"bool","false")
        elif operand_1_type == "string" and operand_2_type == "string":
            result = operand_1_value < operand_2_value
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_GT(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) > int(operand_2_value)
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        elif operand_1_type == "bool" and operand_2_type == "bool":
            if operand_1_value == "true" and operand_2_value == "false":
                set_var(self.arg1_value,"bool","true")
            else:
                set_var(self.arg1_value,"bool","false")
        elif operand_1_type == "string" and operand_2_type == "string":
            result = operand_1_value > operand_2_value
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_EQ(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None        
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        print(">>>",operand_1_value,"<<<")
        print(">>>",operand_2_value,"<<<")

        if operand_1_type == "int" and operand_2_type == "int":
            result = int(operand_1_value) == int(operand_2_value)
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        elif operand_1_type == "bool" and operand_2_type == "bool":
            if (operand_1_value == "true" and operand_2_value == "true") or (operand_1_value == "false" and operand_2_value == "false"):
                set_var(self.arg1_value,"bool","true")
            else:
                set_var(self.arg1_value,"bool","false")
        elif operand_1_type == "string" and operand_2_type == "string":
            result = operand_1_value == operand_2_value
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        elif operand_1_type == "nil" and operand_2_type == "nil":
            set_var(self.arg1_value,"bool","true")
        elif (operand_1_type == "nil" and operand_2_type == "bool") or (operand_1_type == "bool" and operand_2_type == "nil"):             
            set_var(self.arg1_value,"bool","false")
        elif operand_1_type == "nil" and operand_2_type == "int":
            if int(operand_2_type) == 0:
                set_var(self.arg1_value,"bool","true")
            else:
              set_var(self.arg1_value,"bool","false")  
        elif operand_1_type == "int" and operand_2_type == "nil":
            if int(operand_1_type) == 0:
                set_var(self.arg1_value,"bool","true")
            else:
              set_var(self.arg1_value,"bool","false")
        elif operand_1_type == "nil" and operand_2_type == "string":
            if operand_2_type == "":
                set_var(self.arg1_value,"bool","true")
            else:
              set_var(self.arg1_value,"bool","false") 
        elif operand_1_type == "string" and operand_2_type == "nil":
            if operand_1_type == "":
                set_var(self.arg1_value,"bool","true")
            else:
              set_var(self.arg1_value,"bool","false")
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_and(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")              
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "bool" and operand_2_type == "bool":
            operand_1_value = str_to_bool(operand_1_value)
            operand_2_value = str_to_bool(operand_2_value)
            result = operand_1_value and operand_2_value
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_or(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")          
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "bool" and operand_2_type == "bool":
            operand_1_value = str_to_bool(operand_1_value)
            operand_2_value = str_to_bool(operand_2_value)
            result = operand_1_value or operand_2_value
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_not(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")                
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None        
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if operand_1_type == "bool":
            operand_1_value = str_to_bool(operand_1_value)            
            result = not operand_1_value 
            result = bool_to_str(result)
            set_var(self.arg1_value,"bool",result)
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)                      

class IPP_int2char(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")                
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):        
        target_type = None
        target_value = None
        if self.arg2_type == "var":
            target_type,target_value = get_var(self.arg2_value)
        else:
            target_type = self.arg2_type
            target_value = self.arg2_value
        
        if target_type == "int":
            target_value = int(target_value)
            znak = None
            try:
                znak = chr(target_value)
            except :
                print("Nespravna hodnota INT pro Unicode znak",file=sys.stderr)
                exit(58)

            set_var(self.arg1_value,"string",znak) 
        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53) 

class IPP_stri2int(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")  
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        from_type = None
        from_value = None
        position_type = None
        position_value = None
        if self.arg2_type == "var":
            from_type,from_value = get_var(self.arg2_value)
        else:
            from_type = self.arg2_type
            from_value = self.arg2_value
        
        if self.arg3_type == "var":
            position_type,position_value = get_var(self.arg3_value)
        else:
            position_type = self.arg3_type
            position_value = self.arg3_value

        if from_type == "string" and position_type == "int":
            position_value = int(position_value)
            if 0 <= position_value and position_value < len(from_value):            
                znak = from_value[position_value]
                number = ord(znak)
                set_var(self.arg1_value,"int",number)
            else:
                print("Index mimo retezec",file=sys.stderr)
                exit(58) 

        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53) 

class IPP_read(instruction):
    def __init__(self,xml_instr):
        self.print_self()
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")        
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"type")        
        self.store_instruction(int(xml_instr.attrib["order"]))
        
    def run_instruction(self):
        vstup = input()
        typ = self.arg2_value

        if typ == "int":
            try:
                vstup = int(vstup)
            except :
                typ = "nil"
                vstup = "nil"
        elif typ == "string":
            vstup = string_repair(vstup)
        elif typ == "bool":
            if vstup.lower() == "true":
                vstup = "true"
            else:
                vstup = "false"
        else:
            typ = "nil"
            vstup = "nil"
        set_var(self.arg1_value,typ,vstup)

class IPP_write(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"symb")
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        print_type = None
        print_value = None
        if self.arg1_type == "var":
            print_type,print_value = get_var(self.arg1_value)
        else:
            print_type = self.arg1_type
            print_value = self.arg1_value

        if print_type == "int":
            print(int(print_value),end="")
        elif print_type == "bool":
            print(print_value,end="")
        elif print_type == "nil":
            print("",end="")
        else:
            print_value = string_repair(print_value)
            print(print_value,end="") 

class IPP_concat(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None
        result = None
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "string" and operand_2_type == "string":
            result = operand_1_value + operand_2_value
            set_var(self.arg1_value,"string",result)
            
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_strlen(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))
    
    def run_instruction(self):
        target_type = None
        target_value = None
        if self.arg2_type == "var":
            target_type,target_value = get_var(self.arg2_value)      
        else:
            target_type = self.arg2_type
            target_value= self.arg2_value

        if target_type == "string":
            result = string_repair(target_value)
            set_var(self.arg1_value,"int",len(result))

class IPP_getchar(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")          
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None        
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "string" and operand_2_type == "int": 
            operand_2_value = int(operand_2_value)           
            if 0 <= operand_2_value and operand_2_value < len(operand_1_value):            
                znak = operand_1_value[operand_2_value]                
                set_var(self.arg1_value,"string",znak)
            else:
                print("Index mimo retezec",file=sys.stderr)
                exit(58) 
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_setchar(instruction):    
    def __init__(self,xml_instr): 
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        changing_type,changing_value = get_var(self.arg1_value)
        if changing_type != "string":
            print("Index mimo retezec",file=sys.stderr)
            exit(58)
        operand_1_type = None
        operand_1_value = None
        operand_2_type = None
        operand_2_value = None        
        if self.arg2_type == "var":
            operand_1_type,operand_1_value = get_var(self.arg2_value)      
        else:
            operand_1_type = self.arg2_type
            operand_1_value = self.arg2_value

        if self.arg3_type == "var":
            operand_2_type,operand_2_value = get_var(self.arg3_value)      
        else:
            operand_2_type = self.arg3_type
            operand_2_value = self.arg3_value

        if operand_1_type == "int" and operand_2_type == "string": 
            operand_1_value = int(operand_1_value)           
            if 0 <= operand_1_value and operand_1_value < len(changing_value): 
                znak = None           
                try:
                    znak = operand_2_value[0]
                except :
                    print("Index mimo retezec",file=sys.stderr)
                    exit(58) 
                changing_value = list(changing_value)
                changing_value[operand_1_value] = znak
                changing_value = "".join(changing_value)
                set_var(self.arg1_value,"string",changing_value)
            else:
                print("Index mimo retezec",file=sys.stderr)
                exit(58) 
        else:
            print("Spatne typy operandu",file=sys.stderr)
            exit(53)

class IPP_type(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"var")
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb")         
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        target_type = None       
        if self.arg2_type == "var":
            try:
                target_type,_ = get_var(self.arg2_value)                      
            except :
                set_var(self.arg1_value,"string","") 
        else:
            target_type = self.arg2_type            

        set_var(self.arg1_value,"string",target_type)

class IPP_label(instruction):
    def __init__(self,xml_instr):
        global labels
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"label") 
        self.opcode = int(xml_instr.attrib["order"])
        if self.arg1_value in labels:
            print("Label uz existuje: ",self.arg1_value)
            exit(52)
        else:
            labels[self.arg1_value] = self.opcode 
        self.store_instruction(self.opcode)

    def run_instruction(self):
        pass

class IPP_jump(instruction):
    def __init__(self,xml_instr):        
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"label") 
        self.store_instruction(int(xml_instr.attrib["order"]))
    def run_instruction(self):
        global labels
        global instr_walker
        if self.arg1_value in labels:
            instr_walker = labels[self.arg1_value]
        else:
            print("Label nexistuje: ",self.arg1_value,file=sys.stderr)
            exit(52)  

class IPP_jumpifeq(instruction):
    def __init__(self,xml_instr):    
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"label") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")    
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        global labels
        global instr_walker
        if self.arg1_value in labels:
            operand_1_type = None
            operand_1_value = None
            operand_2_type = None
            operand_2_value = None            
            if self.arg2_type == "var":
                operand_1_type,operand_1_value = get_var(self.arg2_value)      
            else:
                operand_1_type = self.arg2_type
                operand_1_value = self.arg2_value

            if self.arg3_type == "var":
                operand_2_type,operand_2_value = get_var(self.arg3_value)      
            else:
                operand_2_type = self.arg3_type
                operand_2_value = self.arg3_value

            if operand_1_type == "nil" or operand_2_type == "nil":
                instr_walker = labels[self.arg1_value]
            elif operand_1_type == "int" and operand_2_type == "int":
                operand_1_value = int(operand_1_value)
                operand_2_value = int(operand_2_value)
                if operand_1_value == operand_2_value:
                    instr_walker = labels[self.arg1_value]
            elif operand_1_type == "string" and operand_2_type == "string":
                if operand_1_value == operand_2_value:
                    instr_walker = labels[self.arg1_value]
            elif operand_1_type == "bool" and operand_2_type == "bool":
                if operand_1_value == operand_2_value:
                    instr_walker = labels[self.arg1_value]
            else:
                print("Spatne operandy podmineneho skoku",self.arg1_value,file=sys.stderr)
                exit(53)          
        else:
            print("Label nexistuje: ",self.arg1_value,file=sys.stderr)
            exit(52)

class IPP_jumpifneq(instruction):
    def __init__(self,xml_instr):    
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"label") 
        self.arg2_type,self.arg2_value = get_argument(xml_instr,2,"symb") 
        self.arg3_type,self.arg3_value = get_argument(xml_instr,3,"symb")    
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        global labels
        global instr_walker
        if self.arg1_value in labels:
            operand_1_type = None
            operand_1_value = None
            operand_2_type = None
            operand_2_value = None            
            if self.arg2_type == "var":
                operand_1_type,operand_1_value = get_var(self.arg2_value)      
            else:
                operand_1_type = self.arg2_type
                operand_1_value = self.arg2_value

            if self.arg3_type == "var":
                operand_2_type,operand_2_value = get_var(self.arg3_value)      
            else:
                operand_2_type = self.arg3_type
                operand_2_value = self.arg3_value

            if operand_1_type == "nil" or operand_2_type == "nil":
                instr_walker = labels[self.arg1_value]
            elif operand_1_type == "int" and operand_2_type == "int":
                operand_1_value = int(operand_1_value)
                operand_2_value = int(operand_2_value)
                if operand_1_value != operand_2_value:
                    instr_walker = labels[self.arg1_value]
            elif operand_1_type == "string" and operand_2_type == "string":
                if operand_1_value != operand_2_value:
                    instr_walker = labels[self.arg1_value]
            elif operand_1_type == "bool" and operand_2_type == "bool":
                if operand_1_value != operand_2_value:
                    instr_walker = labels[self.arg1_value]
            else:
                print("Spatne operandy podmineneho skoku",self.arg1_value,file=sys.stderr)
                exit(53)          
        else:
            print("Label nexistuje: ",self.arg1_value,file=sys.stderr)
            exit(52)

class IPP_exit(instruction):
    def __init__(self,xml_instr):        
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))        
        
    def run_instruction(self):
        exit_code = 0
        exit_type = None
        if self.arg1_type == "var":
            exit_type,exit_code = get_var(self.arg1_value)
        else:
            exit_type = self.arg1_type
            exit_code = self.arg1_value

        if exit_type == "int":
            exit_code = int(exit_code)
            if 0 <= exit_code and exit_code <= 49:                
                exit(exit_code)
            else:
                print("Spatny exitcode",file=sys.stderr)
                exit(57)
        else:
            print("Spatny exitcode",file=sys.stderr)
            exit(57)        

class IPP_dprint(instruction):
    def __init__(self,xml_instr):
        self.arg1_type,self.arg1_value = get_argument(xml_instr,1,"symb")        
        self.store_instruction(int(xml_instr.attrib["order"]))
    def run_instruction(self):
        pass

class IPP_break(instruction):
    def __init__(self,xml_instr):        
        self.store_instruction(int(xml_instr.attrib["order"]))

    def run_instruction(self):
        log_inside()  

#main
#zpracovani argumentu programu
parser = argparse.ArgumentParser(description='Interpret jazyka IPPcode21')
parser.add_argument('--source=', dest='source', type=str, required=False,help='Soubor, odkud se bude cist IPP CODE')
parser.add_argument('--input=', dest='input', type=str, required=False,help='soubor, ze ktereho se bude brat vstup pro kod IPP CODE')
args = parser.parse_args()

#pokud nebyl zadan ani jeden soubor
if args.source == None and args.input == None:
    print("Chybi source soubor nebo input soubor", file=sys.stderr)
    exit(42) #nebyl definovan exit code nebo jsem jej nenasel

source_file = None
input_file = None
#prirazeni/otevreni spravnych souboru podle argumentu
try: 
    if args.source != None and args.input != None:
        source_file = ET.parse(args.source)
        input_file = open(args.input,"r")
    elif args.source != None:
        source_file = ET.parse(args.source)
        input_file = sys.stdin
    else:
        data = sys.stdin.read()        
        source_file = ET.fromstring(data)                
        input_file = open(args.input,"r")       
except:
    print("Nepodarilo se otevrit soubor/y",file=sys.stderr)
    exit(31) 

#podle toho zda byl/nebyl zadan source file musim nastavit koren
if args.source == None:
    root = source_file
    del source_file
else:
    root = source_file.getroot()

#kontrola XML filu na root tag
if root.tag != "program":
    print("Spatny XML: root tag musi byt: program",file=sys.stderr)
    exit(32) 

root_attrib = root.attrib

#kontrola XML filu na pritomnost IPPCODE21
try:
    if root_attrib["language"].upper() != "IPPCODE21":
        print("Spatny jazyk",file=sys.stderr)
        exit(31) 
except:
    print("Chybejici atribut programu: language",file=sys.stderr)
    exit(32)  

#switch na vyber spravne instrukce
def isntr_switch(argument):
    switcher = {
        "MOVE": IPP_move,        
        "CREATEFRAME": IPP_createframe,
        "PUSHFRAME": IPP_pushframe,
        "POPFRAME": IPP_popframe,
        "DEFVAR": IPP_defvar,
        "CALL": IPP_call,
        "RETURN": IPP_return,
        "PUSHS": IPP_pushs,
        "POPS": IPP_pops,
        "ADD": IPP_add,
        "SUB": IPP_sub,
        "MUL": IPP_mul,
        "IDIV": IPP_idiv,
        "LT": IPP_LT,
        "GT": IPP_GT,
        "EQ": IPP_EQ,
        "AND": IPP_and,
        "OR": IPP_or,
        "NOT": IPP_not,
        "INT2CHAR": IPP_int2char,
        "STRI2INT" : IPP_stri2int,
        "READ": IPP_read,
        "WRITE": IPP_write,
        "CONCAT": IPP_concat,
        "STRLEN": IPP_strlen,
        "GETCHAR": IPP_getchar,
        "SETCHAR": IPP_setchar,
        "TYPE": IPP_type,
        "LABEL": IPP_label,
        "JUMP": IPP_jump,
        "JUMPIFEQ": IPP_jumpifeq,
        "JUMPIFNEQ": IPP_jumpifneq,
        "EXIT": IPP_exit,
        "DPRINT": IPP_dprint,
        "BREAK": IPP_break
    }
    return switcher.get(argument,instruction)

#pro kazdou instrukci v XML zkontroluji, zda obsahuje co ma
#a podle nacteneho OPCODE vytvorim objekt instrukce a ten ulozim do instruction_arr
for child in root:    
    if child.tag != "instruction":
        print("Spatny format tagu pro instrukci",file=sys.stderr)
        exit(32)
    try:
        child.attrib["opcode"]
        if child.attrib["order"].isdigit():
            pass 
    except:
        print("Chybi attribut order nebo opcode",file=sys.stderr)
        exit(32)
    for arg in child:   #kontroluji, zda obsahuje pouze argumenty arg1 | arg2 | arg3
        if not(re.fullmatch("arg[1|2|3]",arg.tag)):
            print("spatny argumenty instrukce")
            exit(32)
    instr = isntr_switch(child.attrib["opcode"].upper()) #vyber spravne instrukce  
    
    instr(child) #konstruktor instrukce vezme si XML reprezentaci instrukce i s argumenty, zinicializuje dany objekt(vytvori jej a ulozi si potrebne argumenty) a ulozi se do instruction_arr na index podle sveho order
    #pokud je spatny OPCODE ukonci program


#vykonani instrukci z instruction_arr
#skoky jsou reaalizovany tak, ze instrukce zmeni instr_walker na poradi daneho navesti, na konci cyklu se zvetsi o 1 a zacne se hned vykonavat instrukce za navestim
instr_walker = 0
instr_max_order += 1    #v promene je ulozene nejvyssi poradi, abych vykonal posledni instrukci, musim zvysit o 1 
while instr_walker < instr_max_order:
    if instr_walker in instruction_arr: #pokud existuje, vykona instrukci, pokud ne zvetsi walker a pokracuje
        instruction_arr[instr_walker].run_instruction()
    else:        
        pass   
    instr_walker += 1


