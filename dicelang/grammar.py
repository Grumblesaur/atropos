raw_text = r"""
start: expression (";" expression)* (";")?

identifier_get: identifier
identifier_set: identifier "=" expression
identifier_set_subscript: identifier ("[" expression "]")+ "=" expression

deletable: identifier                       -> deletable_variable
         | identifier ("[" expression "]")+ -> deletable_element
         | identifier ("." identifier    )+ -> deletable_attribute

deletion: "del" deletable ("," deletable)*

assignment: identifier_set
          | identifier_set_subscript
          | identifier ("." identifier)+ "=" expression -> setattr

block: "begin" expression (";" expression)* (";")? "end"

function: "(" (PARAM ("," PARAM)* )? ")" "->" [block | short_body]

for_loop: "for" identifier "in" expression "do" [block | short_body]

while_loop: "while" expression "do" [block | short_body]

do_while_loop: "do" [block | short_body] "while" expression

conditional: "if" expression "then" [block | short_body] -> if
 | "if" expression "then" [block | short_body] "else" [block | short_body] -> if_else

short_body: expression

import: KW_IMPORT identifier                    -> standard_import
      | KW_IMPORT identifier ("." identifier)+  -> standard_getattr_import
      | KW_IMPORT identifier "as" identifier                     -> as_import
      | KW_IMPORT identifier ("." identifier)+ "as" identifier   -> as_getattr_import

alias: identifier "aliases" expression
inspection: KW_INSPECT identifier

expression: assignment
          | deletion
          | block
          | function
          | for_loop
          | while_loop
          | do_while_loop
          | conditional
          | break
          | import
          | alias
          | inspection

break: KW_BREAK break -> break_expr
     | KW_BREAK       -> break_bare
     | print

print: KW_PRINTLN print -> printline
     | KW_PRINT   print -> printword
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

comp: shift (math_comp shift)+ -> comp_math
    | shift (obj_comp shift)+  -> comp_obj
    | shift "in" shift         -> present
    | shift "not" "in" shift   -> absent
    | shift

shift: shift "<<" arithm -> left_shift
     | shift ">>" arithm -> right_shift
     | arithm

arithm: arithm "+" term -> addition
      | arithm "-" term -> subtraction
      | arithm "$" term -> catenation
      | term

term: term "*"  factor -> multiplication
    | term "/"  factor -> division
    | term "%"  factor -> remainder
    | term "//" factor -> floor_division
    | factor

factor: "-" factor -> negation
      | "+" factor -> absolute_value
      | power

power: reduction "**" power -> exponent
     | power "%%" reduction -> logarithm
     | reduction

reduction: "&"  reduction -> sum_or_join
         | "#"  reduction -> length
         | "@"  reduction -> selection
         | "!<" reduction -> minimum
         | "!>" reduction -> maximum
         | "|"  reduction -> flatten
         | "?"  reduction -> stats
         | "<>" reduction -> sort
         | "><" reduction -> shuffle
         | slice

slice: slice ("["            ":"             (":")?           "]") -> whole_slice
     | slice ("[" expression ":"             (":")?           "]") -> start_slice
     | slice ("[" expression ":"              ":"  expression "]") -> start_step_slice
     | slice ("[" expression ":" expression  (":")?           "]") -> start_stop_slice
     | slice ("[" expression ":" expression   ":"  expression "]") -> fine_slice
     | slice ("["            ":" expression  (":")?           "]") -> stop_slice
     | slice ("["            ":" expression   ":"  expression "]") -> stop_step_slice
     | slice ("["            ":"              ":"  expression "]") -> step_slice
     | slice ("[" expression "]")                                  -> not_a_slice
     | application

application: die "-:" application -> apply
           | die

die: die KW_D plugin_op                -> scalar_die_all
   | die KW_D plugin_op KW_H plugin_op -> scalar_die_highest
   | die KW_D plugin_op KW_L plugin_op -> scalar_die_lowest
   | die KW_R plugin_op                -> vector_die_all
   | die KW_R plugin_op KW_H plugin_op -> vector_die_highest
   | die KW_R plugin_op KW_L plugin_op -> vector_die_lowest
   | plugin_op

plugin_op: call_or_atom "::" plugin_op -> plugin_call
         | call_or_atom

call_or_atom: call_or_atom "(" (expression ("," expression)* )? ")" -> function_call
            | get_attribute

get_attribute: regex ("." scoped_identifier)+ -> getattr
             | regex

regex: reflection KW_SEEK reflection -> search
     | reflection KW_LIKE reflection -> match
     | reflection

reflection: KW_TYPEOF reflection -> typeof
          | atom

atom: number_literal
    | boolean_literal
    | string_literal
    | list_literal
    | tuple_literal
    | dict_literal
    | undefined_literal
    | identifier_get
    | "(" expression ")" -> priority

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

IDENT:  /(?!(global|my|our|core|del|like|seek|format|typeof|inspect)\b)[a-zA-Z_]+[a-zA-Z0-9_]*/
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
KW_FORMAT:  "format"
KW_TYPEOF:  "typeof"
KW_GLOBAL:  "global"
KW_BREAK:   "break"
KW_PRINT:   "print"
KW_LIKE:    "like"
KW_SEEK:    "seek"
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

