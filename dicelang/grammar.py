raw_text = r"""
start: expression (";" expression)* (";")?

identifier_get: identifier
identifier_set: identifier "=" expression
identifier_set_subscript: identifier ("[" expression "]")+ "=" expression

deletion: "del" identifier                       -> delete_variable
        | "del" identifier ("[" expression "]")+ -> delete_element

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

expression: assignment
          | deletion
          | block
          | function
          | for_loop
          | while_loop
          | do_while_loop
          | conditional
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

bool_not: "not" bool_not -> logical_not
        | comp

GT:  ">"
GE:  ">="
EQ:  "=="
NE:  "!="
LE:  "<="
LT:  "<"

IS:  "is"
NOT: "not"

math_comp: GT | GE | EQ | NE | LE | LT
obj_comp:  IS | IS NOT

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

power: power "**" reduction -> exponent
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

die: die "d" call_or_atom                   -> scalar_die_all
   | die "d" call_or_atom "h" call_or_atom -> scalar_die_highest
   | die "d" call_or_atom "l" call_or_atom -> scalar_die_lowest
   | die "r" call_or_atom                   -> vector_die_all
   | die "r" call_or_atom "h" call_or_atom -> vector_die_highest
   | die "r" call_or_atom "l" call_or_atom -> vector_die_lowest
   | plugin_op

plugin_op: call_or_atom "::" plugin_op -> plugin_call
         | call_or_atom

call_or_atom: atom "(" (expression ("," expression)* )? ")" -> function_call
            | get_attribute

get_attribute: atom ("." identifier)+ -> getattr
             | atom

atom: number_literal
    | boolean_literal
    | string_literal
    | list_literal
    | dict_literal
    | undefined_literal
    | identifier_get
    | "(" expression ")" -> priority

undefined_literal: UNDEFINED
number_literal:    NUMBER
string_literal:    STRING
boolean_literal:   TRUE | FALSE
list_literal: "[" expression ("," expression)* (",")? "]"  -> populated_list
    | "[" "]"                                              -> empty_list
    | "[" expression "to" expression "]"                   -> range_list
    | "[" expression "to" expression "by" expression "]"   -> range_list_stepped

dict_literal: "{" "}"                                   -> empty_dict
  | "{" key_value_pair ("," key_value_pair)* (",")? "}" -> populated_dict

key_value_pair: expression ":" expression

identifier: scoped_identifier
          | private_identifier
          | server_identifier
          | global_identifier

scoped_identifier:              IDENT
private_identifier:   KW_MY     IDENT
server_identifier:    KW_OUR    IDENT
global_identifier.2:  KW_GLOBAL IDENT

TRUE:      "True"
FALSE:     "False"
UNDEFINED: "Undefined"

KW_GLOBAL: "global"
KW_OUR:    "our"
KW_MY:     "my"

IDENT: /[a-zA-Z_]+[a-zA-Z0-9_]*/
PARAM: /[a-zA-Z_]+[a-zA-Z0-9_]*/
STRING: /("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i

%import common.NUMBER -> NUMBER
%import common.WS
%import common.NEWLINE
%ignore WS
%ignore "`"
COMMENT_INLINE: /\~[^(\n|\r\n|\r)]+/
COMMENT_BLOCK:  /\~\[(.|\n|\r\n|\r)+\]\~/
%ignore COMMENT_INLINE
%ignore COMMENT_BLOCK

"""

