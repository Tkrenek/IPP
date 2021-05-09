<?php
/**
*IPP projekt 1. část - parse.php
*
*Autor: Tomáš Křenek
*Login: xkrene15
*/

/*pole s instrukcemi*/
$instrs = array("MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN",
                "PUSHS", "POPS", "ADD", "SUB", "DPRINT", "MUL", "IDIV", "LT", "GT", "EQ", "OR", "NOT",
                "AND", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR",
                "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "BREAK");

/*funkce pro zjitění instrukce*/
/*hledá řetězec v poli s instrukcemi*/
function isInstruction($prvek) {
    $instrcount = -1;
    global $instrs;
    foreach ($instrs as $inst) {
        if (preg_match("/^".$inst."$/i", $prvek)) {
            $instrcount++;
            break;
        }
    }

    return $instrcount;
}

/*kontrola operandů, zda jsou správného typu*/
/*lexikální kontrola je řešena níže*/

/*zjitění zda se jedná o symb*/
function isSymb($prvek) {
    $symbcount = -1;
    if (preg_match("/^(string|nil|bool|int)@.*$/", $prvek) || preg_match("/^(GF|LF|TF)@.*$/", $prvek)) {
                $symbcount++;
    }
    return $symbcount;
}

/*ověření, zda se jedná o type*/
function isType($prvek) {
    $typecount = -1;
    if (preg_match("/^(int|bool|string)$/", $prvek)) {
        $typecount++;
    }
    return $typecount;
}

/*ověření, zda se jedná o var*/
function isVar($prvek) {
    $varcount = -1;
    if(preg_match("/^(LF|TF|GF)@[A-Za-z_\-&\?!%$*][A-Za-z0-9_\-&\?!%$*]*$/", $prvek)) {
        $varcount++;
    }
    return $varcount;
}

/*ověření, zda se jedná o label*/
function isLabel($prvek) {
    $labelcount = -1;
    if(preg_match("/^[a-zA-Z_\-&\?!%$*][a-zA-Z0-9_\-&\?!%$*]*$/", $prvek)) {
        $labelcount++;
    }
    return $labelcount;
}
/*Vypis help*/
 if($argv[1] == "--help") {
    if($argc == 2) {
        fputs(STDOUT, "Parse.php nacte ze standartniho vstupu kod v jazyce IPPcode20.\n");
		fputs(STDOUT, "Overi lexikalni a syntaktickou spravnost.\n");
        fputs(STDOUT, "Vygeneruje XML soubor.\n");
		exit(0); 
    } else 
        fputs(STDERR, "Bad combination of parametres\n");
        exit(10);
}

$result = "";
$linecount = 0;
$comments = 0;
$stdin = STDIN;
$instrcount = 0;
$instructions = array();
$spaces = array();
$lines = 0;
$comments_active = false;
$instrInOne = 0;

/* čtení ze stdin */
while(!feof($stdin)){
    
    $line = fgets($stdin);

    
    if($linecount == 0) {
        if(preg_match("/^\s*#+.*/", $line) || preg_match("/^\s+$/", $line)) { // pokud je na prvním řádku komentář před hlavičkou
            $line = "\n";
            $skip  = 1;
            $linecount--;
        }
    }

    if($linecount == 0) {

        if(!preg_match("/^\s*\.ippcode20(\n|\s*#+|\s*$)/i", $line)){ // pokud není správná hlavička
            fputs(STDERR, "Bad or missing header\n");
            exit(21);  
        }
    }
    
    if(preg_match(("/^\s*#/"), $line)) {
        $isi++;
    }
    

    if (preg_match("/#/", $line)) { // komentáře
            $comments++;
            $commentline = explode("#", $line);
            $line = $commentline[0];
            
    }

    if(preg_match("/\s*/", $line)) {
        $isi++;
    }
    
    if(($linecount > 0)) {
        
        $line1 = explode(" ", $line); 
            if(isInstruction($line1[0]) > -1 || $line == "") {
                $isi++;
            } 
      
    }

    
    if($linecount > 0) {
        array_push($spaces, $isi);
    }

    $isi = 0;
    $line1 = array();
  
    $linecount++;

   if($line != "" && $line != "\n" && $linecount > 1) {
        if(preg_match("/^\s+#?$/", $line)){
            $isspaces = 1;
        }
        $line = preg_replace("/^\s+/", "", $line);
        $isFirst = explode(" ", $line);
        
               
    if(isInstruction($isFirst[0]) == -1 && $isspaces != 1) { // pokud na začátku řádku není instrukce, chyba 22
           fputs(STDERR, "Bad or missing opcode\n");
           exit(22);
       }  

    
    foreach ($isFirst as $element) {
        if(isInstruction($element) != -1) { // Počítání instrukcí na řádku
             $instrInOne++;
            
        }
    }
       
 }
 $isspaces = 0;

 
    if($instrInOne > 1) { // Pokud je na řádku, více jak jedna instrukce
        fputs(STDERR, "Syn or lex error\n");
        exit(23);
    }
   
    $instrInOne = 0;
 
        
   
    $result = $result . $line . " ";
}

if(in_array(0, $spaces)) {
    fputs(STDERR, "Syn or lex error\n");
    exit(23);
}

$result = trim($result);
$result = preg_replace("/\s+/", " ", $result);

$pole = explode(" ", $result);

/*ověření lexikální správnosti, pokud neodpovídá ničemu správnému, je to chyba*/
foreach ($pole as $prvek) {
    // pokud tam není @
    if(!preg_match("/@/", $prvek)) {
        if(preg_match("/^\.ippcode20$/i", $prvek)) { // hlavička
        } else {
            if(preg_match("/^(string|bool|int)$/", $prvek)) { // typ
            } else {
                if(isInstruction($prvek) != -1) { // instrukce
                    array_push($instructions, $prvek);
                } else {
                    if(preg_match("/^[a-zA-Z_\-&\?!%$*][a-zA-Z0-9_\-&\?!%$*]*$/", $prvek)){ // label
                    } else {
                        fputs(STDERR, "Syn or lex error\n");
                        exit(23);
                    }
                }
            }
        }
    // je tam @
    } else {
        if(preg_match("/^(int|string|bool|nil)/", $prvek)) { // pokud tam je datovy typ
             if ( preg_match("/^bool@(true|false)$/", $prvek) 
                || preg_match("/^int@[+-]?[0-9]+$/", $prvek) || preg_match("/^nil@nil$/", $prvek) || 
                preg_match("/^string@(\\\\[0-9]{3}|[^\\\\])*$/", $prvek)) {
             } else {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
             }
        } else {
           if(preg_match("/^(LF|TF|GF)@[A-Za-z_\-&\?!%$*][A-Za-z0-9_\-&\?!%$*]*$/", $prvek)) {  
           } else {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
           }
        }   
    }
}

/*naplnění pole instrukcemi k porovnávání s počtem operandů*/
$operands = array();
$args = array();
foreach($pole as $prvek2) {
    if(isInstruction($prvek2) != -1) { // pokud je instrukce
        if($instr_tmp != 0) {
            array_push($args, $argcount);
        }
        $instr_tmp++;
        $argcount = 0;
        
    } else {
        $argcount++;
        array_push($operands, $prvek2);
    }   
}
array_push($args, $argcount);


/* kontrola počtu operandů*/
for($i = 0; $i < sizeof($instructions); $i++) {
    switch(strtoupper($instructions[$i])){
        case "JUMPIFEQ":
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
        case "JUMPIFNEQ":
            if($args[$i] != 3) {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            break;
        case "MOVE":
        case "INT2CHAR":
        case "READ":
        case "STRLEN":
        case "NOT":
        case "TYPE":
            if($args[$i] != 2) {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            break;
        case "DEFVAR":
        case "CALL":
        case "PUSHS":
        case "POPS":
        case "WRITE":
        case "LABEL":
        case "JUMP":
        case "EXIT":
        case "DPRINT":
            if($args[$i] != 1) {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            break;
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            if($args[$i] != 0) {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            break;
    }
}
/*Získání typu ze symb*/
function getTy($symb) {
    $type = explode("@", $symb);
    if(preg_match("/^(GF|LF|TF)/", $type[0])) {
        $type[0] = "var";
    }
    return $type[0];
}

/*Získání hodnoty ze symb */
function getValue($symb) {
    $val = explode("@", $symb);

    if(preg_match("/^(GF|LF|TF)/", $val[0])) {
        $val[1] = $symb;
    }
    return $val[1];
}

/*příprava pro generování a generování headeru*/    
$xmlwrite = xmlwriter_open_memory();
xmlwriter_set_indent($xmlwrite, 1);
$res = xmlwriter_set_indent_string($xmlwrite, "    ");
xmlwriter_start_document($xmlwrite, '1.0', 'UTF-8');
xmlwriter_start_element($xmlwrite, 'program');
xmlwriter_start_attribute($xmlwrite, 'language');
xmlwriter_text($xmlwrite, 'IPPcode20');
xmlwriter_end_attribute($xmlwrite);
$instr = 1;

/*kontrola správného typu operandů a následné generování kódu*/
for($i = 1; $i < sizeof($pole); $i++) {
    switch(strtoupper($pole[$i])){
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            if(isLabel($pole[$i+1]) == -1 || isSymb($pole[$i+2]) == -1 || isSymb($pole[$i+3]) == -1) {
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'label');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg2');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+2]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+2]));
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg3');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+3]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+3]));
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $instr++;
            $i = $i + 3;
            break;

        case "ADD":
        case "CONCAT":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "GETCHAR":
        case "SETCHAR":
        case "STRI2INT":
            if(isVar($pole[$i+1]) == -1 || isSymb($pole[$i+2]) == -1 || isSymb($pole[$i+3]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
             xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'var');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg2');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+2]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+2]));
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg3');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+3]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+3]));
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 3;
            $instr++;
            break;
       
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "NOT":
        case "TYPE":
            if(isVar($pole[$i+1]) == -1 || isSymb($pole[$i+2]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'var');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg2');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+2]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+2]));
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 2;
            $instr++;
            break;   
        case "READ":
             if(isVar($pole[$i+1]) == -1 || isType($pole[$i+2]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'var');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);

            xmlwriter_start_element($xmlwrite, 'arg2');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'type');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+2]);
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 2;
            $instr++;
            break;
       
        case "DEFVAR":
        case "POPS":
            if(isVar($pole[$i+1]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'var');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 1;
            $instr++;
        break;
        case "CALL":
        case "LABEL":
        case "JUMP":
            if(isLabel($pole[$i+1]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, 'label');
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, $pole[$i+1]);
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 1;
            $instr++;
        break;
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            if(isSymb($pole[$i+1]) == -1){
                fputs(STDERR, "Syn or lex error\n");
                exit(23);
            }
            xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_start_element($xmlwrite, 'arg1');
            xmlwriter_start_attribute($xmlwrite, 'type');
            xmlwriter_text($xmlwrite, getTy($pole[$i+1]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_text($xmlwrite, getValue($pole[$i+1]));
            xmlwriter_end_element($xmlwrite);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $i = $i + 1;
            $instr++;
            break;
       
        
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
        xmlwriter_start_element($xmlwrite, 'instruction');
            xmlwriter_start_attribute($xmlwrite, 'order');
            xmlwriter_text($xmlwrite, $instr);
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_start_attribute($xmlwrite, 'opcode');
            xmlwriter_text($xmlwrite, strtoupper($pole[$i]));
            xmlwriter_end_attribute($xmlwrite);
            xmlwriter_end_element($xmlwrite);
            $instr++;
        break;
    }   
}
xmlwriter_end_element($xmlwrite); 
xmlwriter_end_document($xmlwrite);
echo xmlwriter_output_memory($xmlwrite);

?>