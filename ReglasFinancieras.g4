<regla> ::= <definicion_variable>? <condicion> '=>' <accion> ';'

<definicion_variable> ::= 'LET' <variable> '=' <expresion> ';'

<variable> ::=  ID;

<condicion> ::= <expresion_booleana> ;

<expresion_booleana> ::= <expresion_relacional>
                      | <expresion_booleana> ('&&' | '||') <expresion_relacional>
                      | '!' <expresion_booleana>
                      | '(' <expresion_booleana> ')'
                      ;

<expresion_relacional> ::= <expresion> <operador_relacional> <expresion>
                        | <expresion> 'IN' <lista>
                        ;

<operador_relacional> ::= '>' | '<' | '>=' | '<=' | '==' | '!=' ;

<expresion> ::= <termino>
              | <expresion> ('+' | '-' | '*' | '/') <termino>
              | '(' <expresion> ')'
              ;

<termino> ::= <variable>
           | <constante>
           | <atributo>
           | <funcion>
           ;

<lista> ::= '[' <constante> (',' <constante>)* ']'
         | ID; // Referencia a una lista predefinida

<constante> ::= NUMBER | STRING | 'true' | 'false' ;

<atributo> ::=  'transaccion.' ID  | 'cliente.' ID | 'cuenta.' ID | 'prestamo.' ID; // Acceso a atributos

<funcion> ::= ID '(' (<expresion> (',' <expresion>)* )? ')' ;

<accion> ::= 'APROBAR'
           | 'RECHAZAR'
           | 'REVISAR'
           | 'BLOQUEAR'
           | 'ALERTAR' '(' STRING ')'
           | 'requiereAprobacion' '(' STRING ')'
           | 'MARCAR_COMO_SOSPECHOSO'
           | <variable> '=' <expresion> // Asignación
           ;

// Tokens (definidos con expresiones regulares, o en ANTLR con reglas léxicas)
ID : [a-zA-Z][a-zA-Z0-9]* ;
NUMBER : [0-9]+ ('.' [0-9]+)? ;
STRING : '\'' ( ~['\\] | '\\' . )* '\'' ; // String con escape
WS : [ \t\r\n]+ -> skip ;