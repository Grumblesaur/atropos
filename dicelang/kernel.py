from dicelang import handlers, ownership
from dicelang.undefined import Undefined

scoping_data = None
datastore = None
identifier_types = (
  'scoped_identifier',
  'private_identifier',
  'server_identifier',
  'global_identifier')

class LoopBreak(Exception):
  pass

def handle_instruction(tree, user='', server='', persistence=None):
  global scoping_data
  global datastore
  if tree.data == 'start':
    scoping_data = ownership.ScopingData(user, server)
    datastore = persistence
    out = [handle_instruction(child) for child in tree.children][-1]
  
  elif tree.data == 'block':
    out = handlers.handle_block(tree.children, scoping_data)
  elif tree.data == 'short_body':
    out = handlers.handle_block(tree.children, scoping_data)  
  elif tree.data == 'function':
    out = handlers.handle_function(tree.children)
 
  elif tree.data == 'for_loop':
    out = handlers.handle_for_loop(tree.children, scoping_data)
  elif tree.data == 'while_loop':
    out = handlers.handle_while_loop(tree.children, scoping_data)
  elif tree.data == 'do_while_loop':
    out = handlers.handle_do_while_loop(tree.children, scoping_data)
  
  elif tree.data == 'conditional':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'if':
    out = handlers.handle_if(tree.children, scoping_data)
  elif tree.data == 'if_else':
    out = handlers.handle_if_else(tree.children, scoping_data)
    
  elif tree.data == 'expression':
    out = handle_instruction(tree.children[0])
  
  elif tree.data == 'deletion':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'delete_variable':
    out = handlers.handle_delete_variable(tree.children)
  elif tree.data == 'delete_element':
    out = handlers.handle_delete_element(tree.children)
  elif tree.data == 'delete_attribute':
    out = handlers.handle_delete_attribute(tree.children)
  
  elif tree.data == 'assignment':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'identifier_set':
    out = handlers.handle_identifier_set(tree.children)
  elif tree.data == 'identifier_set_subscript':
    out = handlers.handle_identifier_set_subscript(tree.children)
  elif tree.data == 'setattr':
    out = handlers.handle_setattr(tree.children)
  
  elif tree.data == 'if_expr':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'inline_if':
    out = handlers.handle_inline_if(tree.children)
  elif tree.data == 'inline_if_binary':
    out = handlers.handle_inline_if_binary(tree.children)
   
  elif tree.data == 'repeat':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'repetition':
    out = handlers.handle_repetition(tree.children)
  
  elif tree.data == 'bool_or':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_or':
    out = handlers.handle_logical_or(tree.children)
  
  elif tree.data == 'bool_xor':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_xor':
    out = handlers.handle_logical_xor(tree.children)
  
  elif tree.data == 'bool_and':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_and':
    out = handlers.handle_logical_and(tree.children)
  
  elif tree.data == 'bool_not':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_not':
    out = handlers.handle_logical_not(tree.children)
  
  elif tree.data == 'comp':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'comp_math':
    out = handlers.handle_comp_math(tree.children)
  elif tree.data == 'comp_obj':
    out = handlers.handle_comp_obj(tree.children)
  elif tree.data == 'math_comp':
    out = tree.children[0].value
  elif tree.data == 'obj_comp':
    kids = tree.children
    is_  = len(kids) == 1
    out = kids[0].value if is_ else f'{kids[0].value} {kids[1].value}'
  elif tree.data == 'present':
    out = handlers.handle_present(tree.children)
  elif tree.data == 'absent':
    out = handlers.handle_present(tree.children, negate=True)
  
  elif tree.data == 'shift':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'left_shift':
    out = handlers.handle_left_shift(tree.children)
  elif tree.data == 'right_shift':
    out = handlers.handle_right_shift(tree.children)
  
  elif tree.data == 'arithm':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'addition':
    out = handlers.handle_addition(tree.children)
  elif tree.data == 'subtraction':
    out = handlers.handle_subtraction(tree.children)
  elif tree.data == 'catenation':
    out = handlers.handle_catenation(tree.children)
  
  elif tree.data == 'term':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'multiplication':
    out = handlers.handle_multiplication(tree.children)
  elif tree.data == 'division':
    out = handlers.handle_division(tree.children)
  elif tree.data == 'remainder':
    out = handlers.handle_remainder(tree.children)
  elif tree.data == 'floor_division':
    out = handlers.handle_floor_division(tree.children)
  
  elif tree.data == 'factor':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'negation':
    out = handlers.handle_negation(tree.children)
  elif tree.data == 'absolute_value':
    out = handlers.handle_absolute_value(tree.children)
  
  elif tree.data == 'power':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'exponent':
    out = handlers.handle_exponent(tree.children)
  elif tree.data == 'logarithm':
    out = handlers.handle_logarithm(tree.children)
  
  elif tree.data == 'reduction':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'sum_or_join':
    out = handlers.handle_sum_or_join(tree.children)
  elif tree.data == 'length':
    out = handlers.handle_length(tree.children)
  elif tree.data == 'selection':
    out = handlers.handle_selection(tree.children)
  elif tree.data in ('minimum', 'maximum'):
    out = handlers.handle_extrema(tree.children, tree.data)
  elif tree.data == 'flatten':
    out = handlers.handle_flatten(tree.children)
  elif tree.data == 'stats':
    out = handlers.handle_stats(tree.children)
  elif tree.data == 'sort':
    out = handlers.handle_sort(tree.children)
  elif tree.data == 'shuffle':
    out = handlers.handle_shuffle(tree.children)
   
  elif tree.data == 'slice':
    out = handle_instruction(tree.children[0])
  elif "_slice" in tree.data:
    out = handlers.handle_slices(tree.data, tree.children)
  
  elif tree.data == 'application':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'apply':
    out = handlers.handle_apply(scoping_data, tree.children)
  
  elif tree.data == 'die':
    out = handle_instruction(tree.children[0])
  elif 'scalar_die' in tree.data or 'vector_die' in tree.data:
    out = handlers.handle_dice(tree.data, tree.children)
  
  elif tree.data == 'plugin_op':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'plugin_call':
    out = handlers.handle_plugin_call(tree.children)
  
  elif tree.data == 'call_or_atom':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'function_call':
    out = handlers.handle_function_call(tree.children, scoping_data)
  
  elif tree.data == 'get_attribute':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'getattr':
    out = handlers.handle_getattr(tree.children)
  
  elif tree.data == 'atom':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'number_literal':
    out = handlers.handle_number_literal(tree.children)
  elif tree.data == 'boolean_literal':
    out = handlers.handle_boolean_literal(tree.children)
  elif tree.data == 'priority':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'populated_list':
    out = handlers.handle_list_literal(tree.children)
  elif tree.data == 'empty_list':
    out = handlers.handle_list_literal(None)
  elif tree.data == 'range_list':
    out = handlers.handle_list_range_literal(tree.children)
  elif tree.data == 'range_list_stepped':
    out = handlers.handle_list_range_literal(tree.children)
  elif tree.data == 'string_literal':
    out = handlers.handle_string_literal(tree.children)
  elif tree.data == 'populated_dict':
    out = handlers.handle_dict_literal(tree.children)
  elif tree.data == 'empty_dict':
    out = handlers.handle_dict_literal(None)
  elif tree.data == 'identifier':
    out = handle_instruction(tree.children[0])
  elif tree.data in identifier_types:
    out = handlers.handle_identifiers(tree.data, tree.children, scoping_data, datastore)
  elif tree.data == 'undefined_literal':
    out = Undefined
  elif tree.data == 'identifier_get':
    ident = handle_instruction(tree.children[0])
    out = ident.get()
  else:
    print(tree.data, tree.children)
    out = '__UNIMPLEMENTED__'
  
  if tree.data == 'start':
    scoping_data = None
    datastore = None
  return out



### DECOMPILE ABSTRACT SYNTAX TREES ###

def binop_decompile(children):
  return (decompile(children[0]), decompile(children[1]))

def passthrough(children):
  return decompile(children[0])

def decompile(tree):
  if tree.data == 'start':
    out = '; '.join([decompile(child) for child in tree.children])
  elif tree.data == 'block':
    expressions = [decompile(child) for child in tree.children]
    exprs = '\t' + ';\n\t'.join(expressions)
    out = f'begin\n{exprs}\nend'
  
  elif tree.data == 'function':
    code = decompile(tree.children[-1])
    params = ', '.join([child.value for child in tree.children[:-1]])
    out = f'({params}) -> {code}'
  
  elif tree.data == 'for_loop':
    iterator = decompile(tree.children[0])
    expression = decompile(tree.children[1])
    code = decompile(tree.children[2])
    out = f'for {iterator} in {expression} do {code}'
  elif tree.data == 'while_loop':
    expression, code = binop_decompile(tree.children)
    out = f'while {expression} do {code}'
  elif tree.data == 'do_while_loop':
    code = decompile(tree.children[0])
    expression = decompile(tree.children[1])
    out = f'do {code} while {expression}'
  
  elif tree.data == 'conditional':
    out = passthrough(tree.children)
  elif tree.data == 'if':
    condition, code = binop_decompile(tree.children)
    out = f'if {condition} then {code}'
  elif tree.data == 'if_else':
    condition, if_code, else_code = [decompile(child) for child in tree.children]
    out = f'if {condition} then {if_code} else {else_code}'
  
  elif tree.data == 'short_body':
    out = decompile(tree.children[0])
  elif tree.data == 'expression':
    out = decompile(tree.children[0])
  elif tree.data == 'deletion':
    out = decompile(tree.children[0])
  elif tree.data == 'delete_variable':
    ident = decompile(tree.children[0])
    out = f'del {ident}'
  elif tree.data == 'delete_element':
    ident = decompile(tree.children[0])
    subscripts = ''.join([f'[{decompile(child)}]' for child in tree.children[1:]])
    out = f'del {ident}{subscripts}'
  elif tree.data == 'assignment':
    out = passthrough(tree.children)
  elif tree.data == 'setattr':
    chain = '.'.join([decompile(child) for child in tree.children[:-1]])
    expression = decompile(tree.children[-1])
    out = f'{chain} = {expression}'
  
  elif tree.data == 'identifier_set':
    ident, expr = binop_decompile(tree.children)
    out = f'{ident} = {expr}'
  elif tree.data == 'identifier_set_subscript':
    identifier = decompile(tree.children[0])
    subscripts = ''.join([f'[{decompile(child)}]' for child in tree.children[1:-1]])
    expression = decompile(tree.children[-1])
    out = f'{identifier}{subscripts} = {expression}'
  elif tree.data == 'identifier_get':
    out = passthrough(tree.children)
  
  elif tree.data == 'if_expr':
    out = decompile(tree.children[0])
  elif tree.data == 'inline_if':
    if_expr = decompile(tree.children[0])
    condition = decompile(tree.children[1])
    else_expr = decompile(tree.children[2])
    out = f'{if_expr} if {condition} else {else_expr}'
  elif tree.data == 'inline_if_binary':
    if_expr, else_expr = binop_decompile(tree.children)
    out = f'{if_expr} if else {else_expr}'
  
  elif tree.data == 'repeat':
    out = decompile(tree.children[0])
  elif tree.data == 'repetition':
    left, right = binop_decompile(tree.children)
    out = f'{left} ^ {right}'
  elif tree.data == 'bool_or':
    out = passthrough(tree.children)
  elif tree.data == 'logical_or':
    left, right = binop_decompile(tree.children)
    out = f'{left} or {right}'

  elif tree.data == 'bool_xor':
    out = passthrough(tree.children)
  elif tree.data == 'logical_xor':
    left, right = binop_decompile(tree.children)
    out = f'{left} xor {right}'

  elif tree.data == 'bool_and':
    out = passthrough(tree.children)
  elif tree.data == 'logical_and':
    left, right = binop_decompile(tree.children)
    out = f'{left} and {right}'

  elif tree.data == 'bool_not':
    out = passthrough(tree.children)
  elif tree.data == 'logical_not':
    operand = decompile(tree.children[1])
    out = f'not {operand}'
  
  elif tree.data == 'comp':
    out = passthrough(tree.children)
  elif tree.data == 'comp_math':
    operands_and_operators = [decompile(child) for child in tree.children]
    out = ' '.join(operands_and_operators)
  elif tree.data == 'math_comp':
    out = tree.children[0].value
  elif tree.data == 'comp_obj':
    out = ' '.join([decompile(child) for child in tree.children])
  elif tree.data == 'obj_comp':
    out = "is" if len(tree.children) == 1 else "is not"
  elif tree.data == 'present':
    left, right = binop_decompile(tree.children)
    out = f'{left} in {right}'
  elif tree.data == 'absent':
    left, right = binop_decompile(tree.children)
    out = f'{left} not in {right}'
  elif tree.data == 'shift':
    out = passthrough(tree.children)
  elif tree.data == 'left_shift':
    left, right = binop_decompile(tree.children)
    out = f'{left} << {right}'
  elif tree.data == 'right_shift':
    left, right = binop_decompile(tree.children)
    out = f'{left} >> {right}'
  
  elif tree.data == 'arithm':
    out = passthrough(tree.children)
  elif tree.data == 'addition':
    left, right = binop_decompile(tree.children)
    out = f'{left} + {right}'
  elif tree.data == 'subtraction':
    left, right = binop_decompile(tree.children)
    out = f'{left} - {right}'
  elif tree.data == 'catenation':
    left, right = binop_decompile(tree.children)
    out = f'{left} $ {right}'
  
  elif tree.data == 'term':
    out = passthrough(tree.children)
  elif tree.data == 'multiplication':
    left, right = binop_decompile(tree.children)
    out = f'{left} * {right}'
  elif tree.data == 'division':
    left, right = binop_decompile(tree.children)
    out = f'{left} / {right}'
  elif tree.data == 'remainder':
    left, right = binop_decompile(tree.children)
    out = f'{left} % {right}'
  elif tree.data == 'floor_division':
    left, right = binop_decompile(tree.children)
    out = f'{left} // {right}'
  
  elif tree.data == 'factor':
    out = passthrough(tree.children)
  elif tree.data == 'negation':
    out = f'-{decompile(tree.children[0])}'
  elif tree.data == 'absolute_value':
    out = f'+{decompile(tree.children[0])}'
  
  elif tree.data == 'power':
    out = passthrough(tree.children)
  elif tree.data == 'exponent':
    left, right = binop_decompile(tree.children)
    out = f'{left} ** {right}'
  elif tree.data == 'logarithm':
    left, right = binop_decompile(tree.children)
    out = f'{left} %% {right}'
  
  elif tree.data == 'reduction':
    out = passthrough(tree.children)
  elif tree.data == 'sum_or_join':
    out = f'&{decompile(tree.children[0])}'
  elif tree.data == 'length':
    out = f'#{decompile(tree.children[0])}'
  elif tree.data == 'selection':
    out = f'@{decompile(tree.children[0])}'
  elif tree.data == 'minimum':
    out = f'!<{decompile(tree.children[0])}'
  elif tree.data == 'maximum':
    out = f'!>{decompile(tree.children[0])}'
  elif tree.data == 'flatten':
    out = f'|{decompile(tree.children[0])}'
  elif tree.data == 'stats':
    out = f'?{decompile(tree.children[0])}'
  elif tree.data == 'sort':
    out = f'<>{decompile(tree.children[0])}'
  elif tree.data == 'shuffle':
    out = f'><{decompile(tree.children[0])}'
  
  elif tree.data == 'slice':
    out = passthrough(tree.children)
  elif tree.data == 'whole_slice':
    out = f'{decompile(tree.children[0])}[:]'
  elif tree.data == 'start_slice':
    indexable, start = binop_decompile(tree.children)
    out = f'{indexable}[{start}:]'
  elif tree.data == 'start_step_slice':
    indexable, start, step = [decompile(child) for child in tree.children]
    out = f'{indexable}[{start}::{step}]'
  elif tree.data == 'start_stop_slice':
    indexable, start, stop = [decompile(child) for child in tree.children]
    out = f'{indexable}[{start}:{stop}]'
  elif tree.data == 'fine_slice':
    indexable, start, stop, step = [decompile(child) for child in tree.children]
    out = f'{indexable}[{start}:{stop}:{step}]'
  elif tree.data == 'stop_slice':
    indexable, stop = binop_decompile(tree.children)
    out = f'{indexable}[:{stop}]'
  elif tree.data == 'stop_step_slice':
    indexable, stop, step = [decompile(child) for child in tree.children]
    out = f'{indexable}[:{stop}:{step}]'
  elif tree.data == 'step_slice':
    indexable, step = binop_decompile(tree.children)
    out = f'{indexable}[::{step}]'
  elif tree.data == 'not_a_slice':
    indexable, index = binop_decompile(tree.children)
    out = f'{indexable}[{index}]'
  
  elif tree.data == 'application':
    out = passthrough(tree.children)
  elif tree.data == 'apply':
    left, right = binop_decompile(tree.children)
    out = f'{left} -: {right}'
  
  elif tree.data == 'die':
    out = passthrough(tree.children)
  elif tree.data == 'scalar_die_all':
    dice, sides = binop_decompile(tree.children)
    out = f'{dice} d {sides}'
  elif tree.data == 'scalar_die_highest':
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = f'{dice} d {sides} h {keep}'
  elif tree.data == 'scalar_die_lowest':
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = f'{dice} d {sides} l {keep}'
  elif tree.data == 'vector_die_all':
    dice, sides = binop_decompile(tree.children)
    out = f'{dice} r {sides}'
  elif tree.data == 'vector_die_highest':
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = f'{dice} r {sides} h {keep}'
  elif tree.data == 'vector_die_lowest':
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = f'{dice} r {sides} l {keep}'
  
  elif tree.data == 'plugin_op':
    out = passthrough(tree.children)
  elif tree.data == 'plugin_call':
    name, operand = binop_decompile(tree.children)
    out = f'{name} :: {operand}'
  
  elif tree.data == 'call_or_atom':
    out = passthrough(tree.children)
  elif tree.data == 'function_call':
    handle = decompile(tree.children[0])
    arguments = ', '.join([decompile(child) for child in tree.children[1:]])
    out = f'{handle}({arguments})'
  
  elif tree.data == 'get_attribute':
    out = passthrough(tree.children)
  elif tree.data == 'getattr':
    obj = decompile(tree.children[0])
    chain = '.'.join([decompile(child) for child in tree.children[1:]])
    out = f'{obj}.{chain}'
  
  elif tree.data == 'atom':
    out = passthrough(tree.children)
  elif tree.data == 'number_literal':
    out = tree.children[-1].value
  elif tree.data == 'string_literal':
    out = tree.children[-1].value
  elif tree.data == 'boolean_literal':
    out = tree.children[-1].value
  elif tree.data == 'undefined_literal':
    out = tree.children[-1].value
  elif tree.data == 'list_literal':
    out = passthrough(tree.children)
  elif tree.data == 'populated_list':
    chain = ', '.join([decompile(child) for child in tree.children])
    out = f'[{chain}]'
  elif tree.data == 'empty_list':
    out = '[]'
  elif tree.data == 'range_list':
    start, stop = binop_decompile(tree.children)
    out = f'[{start} to {stop}]'
  elif tree.data == 'range_list_stepped':
    start, stop, step = [decompile(child) for child in tree.children]
    out = f'[{start} to {stop} by {step}]'
  elif tree.data == 'dict_literal':
    out = passthrough(tree.children)
  elif tree.data == 'empty_dict':
    out = '{}'
  elif tree.data == 'populated_dict':
    chain = ', '.join([decompile(child) for child in tree.children])
    out = '{' + f'{chain}' + '}'
  elif tree.data == 'key_value_pair':
    key, value = binop_decompile(tree.children)
    out = f'{key}: {value}'
  elif tree.data == 'identifier':
    out = passthrough(tree.children)
  elif tree.data == 'scoped_identifier':
    out = tree.children[0].value
  elif tree.data == 'private_identifier':
    out = f'my {tree.children[-1].value}'
  elif tree.data == 'server_identifier':
    out = f'our {tree.children[-1].value}'
  elif tree.data == 'global_identifier':
    out = f'global {tree.children[-1].value}'
  elif tree.data == 'priority':
    out = f'({decompile(tree.children[0])})'
  else:
    print('missed decompiling:', tree.data)
    out = f'__UNIMPLEMENTED__: {tree.data}'
  
  return out


