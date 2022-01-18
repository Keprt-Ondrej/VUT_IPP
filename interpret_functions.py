#!/usr/bin/env python3

#autor: xkeprt03, Ondřej Keprt

import sys
from xml.etree import ElementTree as ET
import re

#kontrola zda je argument symbol
def is_symb(arg_type,arg_value):
    if is_var(arg_type,arg_value) or is_const(arg_type,arg_value):
        return True
    else:
        return False

#kontrola zda je argument promenna
def is_var(arg_type,arg_value):
    if arg_type == "var" and (re.fullmatch('(GF|LF|TF)@[a-z|A-z|_|-|$|&|%|*|!|?][a-z|A-z|_|-|$|&|%|*|!|?|0-9]*',arg_value) != None):    
        return True
    else:
        return False 

#kontrola zda je argument konstanta
def is_const(arg_type,arg_value):
    if arg_type == "string":
        return True
    elif arg_type =="int":
        try:
           arg_value = int(arg_value) #kontrola typu 
        except:
            print("Chyba, typ int nedostane hodnotu int",file=sys.stderr)
            exit(32)
        return True
    elif arg_type == "bool" and (arg_value == "true" or arg_value =="false"):
        return True
    elif arg_type == "nil" and arg_value == "nil":
        return True
    else:
        return False

#kontrola zda je argument navesti
def is_label(arg_type,arg_value):
    if arg_type == "label" and (re.fullmatch('[a-z|A-z|_|-|$|&|%|*|!|?][a-z|A-z|_|-|$|&|%|*|!|?|0-9]*',arg_value)!= None):
        return True
    else:
        return False 

#kontrola zda je argument spravny typ
def is_type(arg_type,arg_value):
    if arg_type == "type" and (re.fullmatch('int|string|bool',arg_value) != None):    
        return True
    else:
        return False    

#funkce pro ziskani argumentu instrukce
#instr = XML reprezentace instrukce
#order = poradi, ktery parametr chci ziskat
#arg_request = pozadavek na kontrolu, zda je argument symb, var atd.
def get_argument(instr,order,arg_request):
    try: 
        #nacteni a ulozeni argumentu
        arg = instr.find('arg'+str(order))
        arg_type = arg.attrib['type'] 
        arg_value = arg.text
    except :
        print("Spatny argument programu",file=sys.stderr)
        exit(32)     
    
    #jednotlive kontroly, zda nactene hodnoty odpovidaji pozadavkum
    if arg_request == "symb":
        if is_symb(arg_type,arg_value):
            return arg_type, arg_value 
        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53)        
    elif arg_request == "var":
        if is_var(arg_type,arg_value):
            return arg_type, arg_value
        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53)   
    elif arg_request == "const":
        if is_const(arg_type,arg_value):
            return arg_type, arg_value
        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53)   
    elif arg_request == "label":
        if is_label(arg_type,arg_value):
            return arg_type, arg_value
        else:
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53) 
    elif arg_request == "type":
        if is_type(arg_type,arg_value):
            return arg_type, arg_value
        else:            
            print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
            exit(53)
    else:        
        print("běhová chyba interpretace – špatné typy operandů",file=sys.stderr)
        exit(53)      
 
#vyjimka
class init_error(Exception):
    pass   

#trida, ktera definuje ramec a praci s nim
class frame:
    def __init__(self):
        self.vars = {}  #zde se budou ukladat jednotlive promenne
        
    #tyto funkce jsou volany z funkci
    # def_var, get_var, set_var, move_var
    def def_var_frame(self,var_name):
        #kontrola zda nebyla promenna v danem ramci jiz definovana
        if var_name in self.vars:
            print("Opakovane definovani promene v jednom ramci: ",var_name,file=sys.stderr)
            exit(52) 
        else:
            self.vars[var_name] = [None] * 2 #definice promenne            

    def get_var_frame(self,var_name):
        #vraci typ,hodnotu      dane promenne
        try:
            if self.vars[var_name][0] != None:
                return self.vars[var_name][0],self.vars[var_name][1]
            else:
                raise  init_error
        except init_error:
            print("Pristup k neicializovane promenne: ",var_name,file=sys.stderr)
            exit(56) 
        except:
            print("Pristup k nedefinovane promenne: ",var_name,file=sys.stderr)
            exit(54) 

    def set_var_frame(self,var_name,value,var_type):
        #nastaveni typu a hodnoty promenne
        try:
            self.vars[var_name][0] = var_type
            self.vars[var_name][1] = value        
        except:
            print("Pristup k nedefinovane promenne: ",var_name,file=sys.stderr)
            exit(54) 
