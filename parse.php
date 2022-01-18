<?php
//autor: Ondrej Keprt
//login: xkeprt03
ini_set('display_errors','STDERR');

//nastaveni navratovych hodnot programu
$success = 0;
$wrong_param = 10;          //chybejici parametr skriptu (je-li treba) nebo použiti zakazane kombinace parametru
$no_header = 21;            //chybná nebo chybejici hlavicka ve zdrojovem kodu zapsanem v IPPcode21;   
$wrong_op_code = 22;        //neznamy nebo chybny operačni kod ve zdrojovem kodu zapsanem v IPPcode21;
define("LEX_SYN_ERR", 23);  //jina lexikalni nebo syntakticka chyba zdrojoveho kodu zapsaneho v IPPcode21.

//zpracovani parametru programu
if (1 <$argc ){
    if (2 < $argc){
        error_log("prilis mnoho parametru\n");
        exit($wrong_param);
    } 

    if ($argv[1] == "--help"){        
        echo "php7.4 parse.php\n";
        echo "\tnacte ze standardniho vstupu zdrojovy kod v IPP-code21,\n\tzkontroluje lexikalni a syntaktickou spravnost kodu\n\ta vypise na standardni vystup XML reprezentaci programu dle specifikace\n\n";
        echo "php7.4 parse.php --help\n";
        echo "\t vypise tuto napovedu\n";
        exit($success); 
    }
    else{
        echo "spatny parametr\n";
        exit($wrong_param);
    }     
}

//hledani hlavicky souboru
$header = false;    //jeste jsem hlavicku nenasel
while ($line = fgets(STDIN)){
    $line = explode('#',$line,2); //odstraneni komentaru
    $line = $line[0];   //prevod na string
    $line = trim($line); //odstraneni koncu radku a mezer na konci radku, pozor na prazdne retezce pri prazdnem radku    
    if(!$header){
        if (strtoupper($line) == ".IPPCODE21"){
            $header = true;
            echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"; 
            echo "<program language=\"IPPcode21\">\n"; 
            break;
        }            
    }
}

if (!$header){
    error_log("Nenalezena hlavicka .IPPCODE21");
    exit($no_header); 
}

//nacteni funkci pro zpracovani zdrojoveho kodu
require 'functions.php';
//echo je zde potreba, z neznameho duvodu mi to pri dalsim
//pouziti echo vytiskne mezeru, stane se tak po require 'functions.php'
// pritom tam vypis pouzivam pouze ve funkci, ne na prazdno...
//timhle se to "zamaskuje"
echo ""; 

$inst_counter = 1;
while ($line = fgets(STDIN)){ 
    $line = explode('#',$line,2);   //odstraneni komentaru
    $line = $line[0];               //prevod na string
    $line = trim($line);                            //odstraneni koncu radku a mezer na konci radku, pozor na prazdne retezce pri prazdnem radku    
    $line = preg_replace('/\s\s+/', ' ', $line);    //redukce tabu a mezer na jednu mezeru 
    $tokens = explode(' ',$line);   //rozdeleni na jednotlive lexikalni tokeny    
    $tokens[0] = strtoupper($tokens[0]); 

    //switch podle prvniho prvku v poli zavola prislusnou funkci na dokonceni instrukce
    //instrukce sama vypisuje
    //VAROVANI - funkce zvetsuji pocitadlo instrukci!
    switch ($tokens[0]){       
        case 'MOVE':
        case 'INT2CHAR':
        case 'STRLEN':
        case 'NOT':
        case 'TYPE':            
            inst_move_int2char_strlen_not_type($tokens, $inst_counter);            
        break;

        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':           
            inst_create_push_pop_frame_break_return($tokens, $inst_counter);
        break; 

        case 'DEFVAR':
        case 'POPS':
            inst_defvar_pops($tokens, $inst_counter);
        break;

        case 'CALL':
        case 'LABEL':
        case 'JUMP':            
            inst_call_label_jump($tokens, $inst_counter);
        break;

        case 'PUSHS':
        case 'WRITE':
        case 'EXIT':
        case 'DPRINT':
            inst_pushs_exit_dprint_write($tokens, $inst_counter);
        break;

        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':        
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
            inst_add_sub_mul_idiv_stri2int_concat_getchar_setchar_lt_gt_eq_and_or($tokens, $inst_counter);
        break;

        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':
            inst_jumpifeq_jumpifneq($tokens, $inst_counter);
        break;

        case 'READ':
            inst_read($tokens, $inst_counter);
        break;

        case "\0":
        case "\n":
        case '':
        case "": //pokud byl prazdny radek nebo komentar na radku, pokracuje se nactenim dalsiho radku             
        break;  

        default:
            error_log("spatny/chybny opcode: ".$tokens[0]); //pokud nenajdu spravnou instrukci        
            exit($wrong_op_code);            
        break;
    } //konec switche na rozdeleni
} //konec cyklu, co nacita radky

echo("</program>\n");
exit($success);
?>