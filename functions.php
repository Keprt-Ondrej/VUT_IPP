<?php
//autor: Ondrej Keprt
//login: xkeprt03

//funkce, ktera zasituje jestli byl jeji parametr promenna
//je volana pokazde pred print_var_XML
function is_var($identif){  
    if (preg_match("/(LF|TF|GF)@([a-z|A-z|_|-|$|&|%|*|!|?]|[a-z|A-z|_|-|$|&|%|*|!|?][a-z|A-z|0-9|_|-|$|&|%|*|!|?])/",$identif)){ 
        return true;
    }
    else return false; 
}

//funkce, ktera zasituje jestli byl jeji parametr navesti
//je volana pokazde pred print_label_XML
function is_label($label){ 
    if (preg_match("/[a-z|A-z|_|-|$|&|%|*|!|?]|[a-z|A-z|_|-|$|&|%|*|!|?][a-z|A-z|0-9|_|-|$|&|%|*|!|?]/",$label)){ 
        return true; 
    }
    else return false; 
}

//funkce, ktera zasituje jestli byl jeji parametr promenna
//je volana pokazde pred print_const_XML
function is_const($const){ 
    $const = explode("@",$const);
    switch($const[0]){ //podle hodnoty pred @ urcim zda je validni konec
        case "int":            
            if(intval($const[1]) || $const[1] == 0){   
                error_log("was here".$const[1]);             
                return true;
            }
            else return false;
        break;

        case "bool":
            if ($const[1] == "true" | $const[1] == "false"){                
                return true;
            }
            else return false;
        break;

        case "string":
            return true;
        break;

        case "nil":
            if ($const[1] == "nil"){                
                return true;
            }
            else return false; 
        break;
        
        default: return false;
    }//konec switche na porovnavani konce    
}//konec funkce is_const()

//funkce, ktera zasituje jestli byl jeji parametr symbol
//je volana pokazde pred print_symb_XML
function is_symb($symb){
    if (is_const($symb) || is_var($symb)) return true;
    else return false;
}

//funkce vypise zacatek instrukce
//VAROVANi - meni pocitadlo instrukci!
function print_start_inst_XML($opcode,&$inst_counter){
    echo "\t<instruction order=\"$inst_counter\" opcode=\"".$opcode."\">\n";
    $inst_counter++;
}

//funkce vypise konec instrukce
function print_end_inst_XML(){
    echo "\t</instruction>\n";
}

//funkce vypise poradi argumentu, ktere je predano pomoci $position a vypise promennou
function print_var_XML($var, $position){    
    echo "\t\t<arg".$position." type=\"var\">".$var."</arg".$position.">\n";
}

//funkce vypise poradi argumentu, ktere je predano pomoci $position a vypise konstantu
function print_const_XML($const, $position){  
    $const = explode("@",$const);
    if ($const[0] == "string"){
        //osetreni stringu pro <> &, to co nema byt v XML
        $const[1] =str_replace("\\038","&amp;", $const[1]);
        $const[1] =str_replace("&","&amp;", $const[1]); 
        $const[1] = str_replace("\\060","&lt;", $const[1]);
        $const[1] = str_replace("<","&lt;", $const[1]);        
        $const[1] =str_replace("\\062","&gt;", $const[1]);
        $const[1] =str_replace(">","&gt;", $const[1]); 
    }
    
    echo "\t\t<arg".$position." type=\"".$const[0]."\">".$const[1]."</arg".$position.">\n";
}

//funkce vypise poradi argumentu, ktere je predano pomoci $position a vypise symbol
function print_symb_XML($symb, $position){
    if (is_var($symb)){
        print_var_XML($symb,$position); 
    }
    else if(is_const($symb)){
        print_const_XML($symb,$position); 
    }
    else{
       error_log("spatny parametr pro vypis symbolu");
       exit(LEX_SYN_ERR); 
    }        
}

//funkce vypise poradi argumentu, ktere je predano pomoci $position a vypise navesti
function print_label_XML($label,$position){
    echo "\t\t<arg".$position." type=\"label\">".$label."</arg".$position.">\n"; 
}

//pokud funkce dostanou nespravny pocet parametru, vypise chybovou hlasku a ukonci program
function wrong_number_param($opcode){
    error_log("spatny pocet parametru pro $opcode");
    exit(LEX_SYN_ERR);
}

//pokud funkce dostanou nespravny typ parametru, vypise chybovou hlasku a ukonci program
function bad_type_param($opcode){
    error_log("spatny typ parametru pro $opcode");
    exit(LEX_SYN_ERR);
}

//pro dalsi funkce plati:
//parametr symbol je oznaceni pro konstantu nebo promennou

//funkce ktera obsluhuje instrukce s parametry promenna a symbol
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_move_int2char_strlen_not_type($tokens, &$inst_counter){       
    if (sizeof($tokens) == 3){
        print_start_inst_XML($tokens[0],$inst_counter);
        if (is_var($tokens[1])){
            print_var_XML($tokens[1],1); 
        } 
        else bad_type_param($tokens[0]);

        if (is_symb($tokens[2])){
            print_symb_XML($tokens[2],2);
        }
        else bad_type_param($tokens[0]);     

        print_end_inst_XML(); 
    }
    else wrong_number_param($tokens[0]);      
}

//funkce ktera obsluhuje instrukce bez parametru
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_create_push_pop_frame_break_return($tokens, &$inst_counter){
    if (sizeof($tokens) == 1){
        print_start_inst_XML($tokens[0],$inst_counter);
        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);
}

//funkce ktera obsluhuje instrukce s parametrem promenna
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_defvar_pops($tokens, &$inst_counter){
    if(sizeof($tokens) == 2){
        print_start_inst_XML($tokens[0],$inst_counter);
        if (is_var($tokens[1])){
            print_var_XML($tokens[1],1);
        }
        else bad_type_param($tokens[0]);

        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);  
}

//funkce ktera obsluhuje instrukce s parametrem navesti
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_call_label_jump($tokens, &$inst_counter){
    if(sizeof($tokens) == 2){   
        print_start_inst_XML($tokens[0],$inst_counter);     
        if (is_label($tokens[1])){            
            print_label_XML($tokens[1],1);
        }
        else bad_type_param($tokens[0]);

        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);
}

//funkce ktera obsluhuje instrukce s parametrem symbol
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_pushs_exit_dprint_write($tokens, &$inst_counter){
    if (sizeof($tokens) == 2){ 
        print_start_inst_XML($tokens[0],$inst_counter);       
        if (is_symb($tokens[1])){
            print_symb_XML($tokens[1],1);
        }
        else bad_type_param($tokens[0]);
        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);     
}

//funkce ktera obsluhuje instrukce s parametrey promenna, symbol a symbol
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_add_sub_mul_idiv_stri2int_concat_getchar_setchar_lt_gt_eq_and_or($tokens, &$inst_counter){
    if (sizeof($tokens) == 4){
        print_start_inst_XML($tokens[0],$inst_counter); 
        if (is_var($tokens[1])){
            print_var_XML($tokens[1],1);
        } 
        else bad_type_param($tokens[0]);
        
        if (is_symb($tokens[2])){
            print_symb_XML($tokens[2],2);
        }
        else bad_type_param($tokens[0]);

        if (is_symb($tokens[3])){
            print_symb_XML($tokens[3],3);
        }
        else bad_type_param($tokens[0]);

        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);
}

//funkce ktera obsluhuje instrukci READ , ma jako parametr promennou a datovy typ
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_read($tokens, &$inst_counter){
    if (sizeof($tokens) == 3){
       print_start_inst_XML($tokens[0],$inst_counter);
        if (is_var($tokens[1])){
            print_var_XML($tokens[1],1);
        }
        else bad_type_param($tokens[0]);

        switch ($tokens[2]){ //kontrola, zda byl zadan validni datovy typ
            case "int":
            case "string":
            case "bool":
                echo "\t\t<arg2 type=\"type\">".$tokens[2]."</arg2>\n";
            break;             
            default:
                bad_type_param($tokens[0]);
            break;
        }
       print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);
}

//funkce ktera obsluhuje instrukce podminenych skoku s parametry navesti, symbol a symbol
//funkce vypise pomoci volani jinych funkci zacatek a konec instrukce a jeji parametry
//nebo ukonci program pri chybnych parametrech nebo pri chybnem poctu parametru
function inst_jumpifeq_jumpifneq($tokens, &$inst_counter){
    if (sizeof($tokens) == 4){
        print_start_inst_XML($tokens[0],$inst_counter); 
        if (is_label($tokens[1])){
            print_label_XML($tokens[1],1);
        } 
        else bad_type_param($tokens[0]);
        
        if (is_symb($tokens[2])){
            print_symb_XML($tokens[2],2);
        }
        else bad_type_param($tokens[0]);

        if (is_symb($tokens[3])){
            print_symb_XML($tokens[3],3);
        }
        else bad_type_param($tokens[0]);

        print_end_inst_XML();
    }
    else wrong_number_param($tokens[0]);
}

?>