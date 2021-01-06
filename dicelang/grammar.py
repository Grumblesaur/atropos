raw_text = r"""
start: expression (";" expression)* (";")?

identifier_get: identifier

assignment: identifier_set | subscript_set
identifier_set: identifier "=" expression
subscript_set:  identifier subscript_chain "=" expression

subscript_chain: subscript+
subscript: "[" expression "]"    -> bracket_subscript
         | "." scoped_identifier -> identifier_subscript

deletion: "del" deletable ("," deletable)*
deletable: identifier                 -> identifier_deletable
         | identifier subscript_chain -> subscript_deletable

body: block | short_body
block: "begin" expression (";" expression)* (";")? "end"
short_body: expression

function: "(" (PARAM ("," PARAM)* )? ")" "->" body

for_loop:      "for"   identifier "in"    expression "do" body
while_loop:    "while" expression "do"    body
do_while_loop: "do"    body       "while" expression

conditional: "if" expression "then" body             -> if
           | "if" expression "then" body "else" body -> if_else

import: KW_IMPORT identifier                    -> standard_import
 | KW_IMPORT identifier ("." identifier)+  -> standard_getattr_import
 | KW_IMPORT identifier "as" identifier                     -> as_import
 | KW_IMPORT identifier ("." identifier)+ "as" identifier   -> as_getattr_import

expression: assignment
          | deletion
          | block
          | function
          | for_loop
          | while_loop
          | do_while_loop
          | conditional
          | import
          | alias
          | keyword_expr

alias: identifier "aliases" expression

keyword_expr: KW_PRINTLN if_expr    -> printline
            | KW_PRINT if_expr      -> printword
            | KW_BREAK if_expr      -> break_expr
            | KW_BREAK              -> break_bare
            | KW_SKIP  if_expr      -> skip_expr
            | KW_SKIP               -> skip_bare
            | KW_RETURN if_expr     -> return_expr
            | KW_RETURN             -> return_bare
            | KW_INSPECT identifier -> inspection
            | if_expr

if_expr: repeat "if" repeat "else" if_expr -> inline_if
       | repeat "if"        "else" if_expr -> inline_if_binary
       | repeat

repeat: repeat "^" bool_or -> repetition
      | bool_or

bool_or: bool_or "or" bool_xor -> logical_or
       | bool_xor

bool_xor: bool_xor "xor" bool_and -> logical_xor
        | bool_and

bool_and: bool_and "and" bool_not -> logical_and
        | bool_not

bool_not: NOT bool_not -> logical_not
        | comp

comp: arithm (math_comp arithm)+ -> comp_math
    | arithm (obj_comp arithm)+  -> comp_obj
    | arithm "in" arithm         -> present
    | arithm "not" "in" arithm   -> absent
    | arithm

arithm: arithm "+" term -> addition
      | arithm "-" term -> subtraction
      | arithm "$" term -> catenation
      | term

term: term "*"  factor -> multiplication
    | term "/"  factor -> division
    | term "%"  factor -> remainder
    | term "//" factor -> floor_division
    | term "<<" factor -> left_shift
    | term ">>" factor -> right_shift
    | factor

factor: "-" factor -> negation
      | "+" factor -> real_part_or_nop
      | power

power: reduction "**" power -> exponent
     | power "%%" reduction -> logarithm
     | reduction

reduction: "&"  reduction -> sum_or_join
         | "#"  reduction -> length
         | "@"  reduction -> selection
         | "!<" reduction -> minimum
         | "!>" reduction -> maximum
         | "?"  reduction -> stats
         | "<>" reduction -> sort
         | "><" reduction -> shuffle
         | die

die: die KW_D primary              -> scalar_die_all
   | die KW_D primary KW_H primary -> scalar_die_highest
   | die KW_D primary KW_L primary -> scalar_die_lowest
   | die KW_R primary              -> vector_die_all
   | die KW_R primary KW_H primary -> vector_die_highest
   | die KW_R primary KW_L primary -> vector_die_lowest
   | primary

primary: primary "." scoped_identifier -> getattr
       | primary "(" (expression ("," expression)* (",")?)? ")" -> function_call
       | primary "[" slice "]" -> sliced
       | KW_TYPEOF primary -> typeof
       | atom "-:" primary -> apply
       | atom "::" primary -> plugin_call
       | atom KW_SEEK primary -> search
       | atom KW_LIKE primary -> match
       | atom

slice:  ":" (":")?                                -> whole_slice
     |  expression ":" (":")?                     -> start_slice
     |  expression ":" ":" expression             -> start_step_slice
     |  expression ":" expression (":")?          -> start_stop_slice
     |  expression ":" expression ":"  expression -> fine_slice
     |  ":" expression (":")?                     -> stop_slice
     |  ":" expression  ":" expression            -> stop_step_slice
     |  ":" ":" expression                        -> step_slice
     |  expression                                -> not_a_slice

atom: number_literal
    | boolean_literal
    | string_literal
    | list_literal
    | tuple_literal
    | dict_literal
    | undefined_literal
    | identifier_get
    | "(" expression ")" -> priority
    | "|" expression "|" -> flatten_or_abs

undefined_literal: UNDEFINED
number_literal:    REAL | COMPLEX
string_literal:    STRING
boolean_literal:   TRUE | FALSE

list_literal: "[" expression ("," expression)* (",")? "]"  -> populated_list
  | "[" "]"                                                -> empty_list
  | "[" expression "to" expression "]"                     -> range_list
  | "[" expression "to" expression "by" expression "]"     -> range_list_stepped
  | "[" expression ("through"|"thru") expression   "]"     -> closed_list
  | "[" expression ("through"|"thru") expression "by" expression "]" -> closed_list_stepped

tuple_literal: "(" expression                    ","   ")" -> mono_tuple
             | "(" expression ("," expression)+ (",")? ")" -> multi_tuple
             | "("                                     ")" -> empty_tuple

dict_literal: "{" "}"                                   -> empty_dict
  | "{" key_value_pair ("," key_value_pair)* (",")? "}" -> populated_dict

key_value_pair: expression ":" expression

identifier: scoped_identifier
          | private_identifier
          | server_identifier
          | global_identifier
          | core_identifier

scoped_identifier:             IDENT
private_identifier:  KW_MY     IDENT
server_identifier:   KW_OUR    IDENT
global_identifier:   KW_GLOBAL IDENT
core_identifier:     KW_CORE   IDENT

TRUE:      "True"
FALSE:     "False"
UNDEFINED: "Undefined"

IDENT:  /(?!(global|my|our|core|del|like|seek|format|typeof|inspect|skip|break|return)\b)[a-zA-Z_]+[a-zA-Z0-9_]*/
PARAM:  /[a-zA-Z_]+[a-zA-Z0-9_]*/
STRING: /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

GT:  ">"
GE:  ">="
EQ:  "=="
NE:  "!="
LE:  "<="
LT:  "<"

KW_PRINTLN: "println"
KW_INSPECT: "inspect"
KW_IMPORT:  "import"
KW_RETURN:  "return"
KW_FORMAT:  "format"
KW_TYPEOF:  "typeof"
KW_GLOBAL:  "global"
KW_BREAK:   "break"
KW_PRINT:   "print"
KW_LIKE:    "like"
KW_SEEK:    "seek"
KW_SKIP:    "skip"
KW_CORE:    "core"
KW_OUR:     "our"
KW_MY:      "my" 
KW_R:       "r"
KW_D:       "d"
KW_H:       "h"
KW_L:       "l"

IS:  /\bis\b/
NOT: /\bnot\b/

math_comp: GT | GE | EQ | NE | LE | LT
obj_comp:  IS | IS NOT



%import common.NUMBER -> REAL
COMPLEX: REAL ["j"|"J"]
%import common.WS
%import common.NEWLINE
%ignore WS
%ignore "`"
COMMENT_INLINE: /~.*/
COMMENT_BLOCK:  "~[" /(.|\n)+/ "]~"
%ignore COMMENT_INLINE
%ignore COMMENT_BLOCK

"""

