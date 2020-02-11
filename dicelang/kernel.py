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
    out = kids[0].value if is_ else '{} {}'.format(kids[0].value, kids[1].value)
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
    block = "begin\n{exprs}end"
    expressions = [ ]
    for child in tree.children:
      expressions.append(decompile(child))
    block.format(exprs=';\n\t'.join(expressions))
    out = block
  elif tree.data == 'function':
    function = '({params}) -> {code}'
    code = decompile(tree.children[-1])
    params = [child.value for child in tree.children[1:-1]]
    out = function.format(params=params, code=code)
  
  elif tree.data == 'for_loop':
    for_loop = 'for {iterator} in {expression} do {code}'
    iterator = tree.children[0].value
    expression = decompile(tree.children[1])
    code = decompile(tree.children[2])
    out = for_loop.format(iterator=iterator, expression=expression, code=code)
  elif tree.data == 'while_loop':
    while_loop = 'while {expression} do {code}'
    expression, code = binop_decompile(tree.children)
    out = while_loop.format(expression=expression, code=code)
  elif tree.data == 'do_while_loop':
    do_while_loop = 'do {code} while {expression}'
    code, expression = binop_decompile(tree.children)
    out = do_while_loop.format(expression=expression, code=code)
  
  elif tree.data == 'conditional':
    out = passthrough(tree.children)
  elif tree.data == 'if':
    if_construct = 'if {condition} then {code}'
    condition = decompile(tree.children[0])
    code = decompile(tree.children[1])
    out = if_construct.format(condition=condition, code=code)
  elif tree.data == 'if_else':
    if_else_construct = 'if {condition} then {if_code} else {else_code}'
    condition = decompile(tree.children[0])
    if_code = decompile(tree.children[1])
    else_code = decompile(tree.children[2])
    out = if_else_construct.format(
      condition=condition,
      if_code=if_code,
      else_code=else_code)
  
  elif tree.data == 'short_body':
    out = decompile(tree.children[0])
  elif tree.data == 'expression':
    out = decompile(tree.children[0])
  elif tree.data == 'deletion':
    out = decompile(tree.children[0])
  elif tree.data == 'delete_variable':
    out = 'del {identifier}'.format(identifier=tree.children[0].value)
  elif tree.data == 'delete_element':
    delete_element = 'del {identifier}{subscripts}'
    ident = tree.children[0].value
    subscripts = ['[{}]'.format(decompile(child)) for child in tree.children[1:]]
    out = delete_element.format(
      identifier=ident,
      subscripts=''.join(subscripts))
  elif tree.data == 'assignment':
    out = passthrough(tree.children)
  elif tree.data == 'setattr':
    set_attr = '{identifier_chain} = {expression}'
    identifier_chain = '.'.join([decompile(child) for child in tree.children[:-1]])
    expression = decompile(tree.children[-1])
    out = set_attr(identifier_chain=identifier_chain, expression=expression)
  elif tree.data == 'identifier_set':
    identifier_set = '{identifier} = {expression}'
    ident, expr = binop_decompile(tree.children)
    out = identifier_set(identifier=ident, expression=expr)
  elif tree.data == 'identifier_set_subscript':
    identifier_set_subscript = '{identifier}{subscripts} = {expression}'
    identifier = decompile(tree.children[0])
    subscripts = ''.join(['[{}]'.format(decompile(child)) for child in children[1:-1]])
    expression = decompile(tree.children[-1])
    out = identifier_set_subscript(
      identifier=identifier,
      subscritps=subscripts,
      expression=expression)
  elif tree.data == 'identifier_get':
    out = passthrough(tree.children)
  
  elif tree.data == 'if_expr':
    out = decompile(tree.children[0])
  elif tree.data == 'inline_if':
    inline_if = '{if_expr} if {condition} else {else_expr}'
    if_expr = decompile(tree.children[0])
    condition = decompile(tree.children[1])
    else_expr = decompile(tree.children[2])
    out = inline_if(if_expr=if_expr, condition=condition, else_expr=else_expr)
  elif tree.data == 'inline_if_binary':
    inline_if_binary = '{if_expr} if else {else_expr}'
    if_expr, else_expr = binop_decompile(tree.children)
    out = inline_if_binary.format(if_expr=if_expr, else_expr=else_expr)
  
  elif tree.data == 'repeat':
    out = decompile(tree.children[0])
  elif tree.data == 'repetition':
    repetition = '{left} ^ {right}'
    left, right = binop_decompile(tree.children)
    out = repetition.format(left=left, right=right)
  
  elif tree.data == 'bool_or':
    bool_or = '{left} or {right}'
    left, right = binop_decompile(tree.children)
    out = bool_or.format(left=left, right=right)
  elif tree.data == 'bool_xor':
    bool_xor = '{left} xor {right}'
    left, right = binop_decompile(tree.children)
    out = bool_xor.format(left=left, right=right)
  elif tree.data == 'bool_and':
    bool_and = '{left} and {right}'
    left, right = binop_decompile(tree.children)
    out = bool_and.format(left=left, right=right)
  elif tree.data == 'bool_not':
    bool_not = 'not {operand}'
    operand = decompile(tree.children[0])
    out = bool_not.format(operand=operand)
  
  elif tree.data == 'comp':
    out = passthrough(tree.children)
  elif tree.data == 'comp_math':
    operands_and_operators = [decompile(child) for child in tree.children]
    out = ' '.format(operands_and_operators)
  elif tree.data == 'math_comp':
    out = tree.children[0].value
  elif tree.data == 'comp_obj':
    operands_and_operators = [decompile(child) for child in tree.children]
    out = ' '.format(operands_and_operators)
  elif tree.data == 'obj_comp':
    out = "is" if len(tree.children) == 1 else "is not"
  elif tree.data == 'present':
    present = '{left} in {right}'
    left, right = binop_decompile(tree.children)
    out = present.format(left=left, right=right)
  elif tree.data == 'absent':
    absent = '{left} not in {right}'
    left, right = binop_decompile(tree.children)
    out = absent.format(left=left, right=right)
  
  elif tree.data == 'shift':
    out = passthrough(tree.children)
  elif tree.data == 'left_shift':
    left_shift = '{left} << {right}'
    left, right = binop_decompile(tree.children)
    out = left_shift.format(left=left, right=right)
  elif tree.data == 'right_shift':
    right_shift = '{left} >> {right}'
    left, right = binop_decompile(tree.children)
    out = right_shift.format(left=left, right=right)
  
  elif tree.data == 'arithm':
    out = passthrough(tree.children)
  elif tree.data == 'addition':
    addition = '{left} + {right}'
    left, right = binop_decompile(tree.children)
    out = addition.format(left=left, right=right)
  elif tree.data == 'subtraction':
    subtraction = '{left} - {right}'
    left, right = binop_decompile(tree.children)
    out = subtraction.format(left=left, right=right)
  elif tree.data == 'catenation':
    catenation = '{left} $ {right}'
    left, right = binop_decompile(tree.children)
    out = catenation.format(left=left, right=right)
  
  elif tree.data == 'term':
    out = passthrough(tree.children)
  elif tree.data == 'multiplication':
    multiplication = '{left} * {right}'
    left, right = binop_decompile(tree.children)
    out = multiplication.format(left=left, right=right)
  elif tree.data == 'division':
    division = '{left} / {right}'
    left, right = binop_decompile(tree.children)
    out = division.format(left=left, right=right)
  elif tree.data == 'remainder':
    remainder = '{left} % {right}'
    left, right = binop_decompile(tree.children)
    out = remainder.format(left=left, right=right)
  elif tree.data == 'floor_division':
    floor_division = '{left} // {right}'
    left, right = binop_decompile(tree.children)
    out = floor_division.format(left=left, right=right)
  
  elif tree.data == 'factor':
    out = passthrough(tree.children)
  elif tree.data == 'negation':
    out = '-{}'.format(decompile(tree.children[0]))
  elif tree.data == 'absolute_value':
    out = '+{}'.format(decompile(tree.children[0]))
  
  elif tree.data == 'reduction':
    out = passthrough(tree.children)
  elif tree.data == 'sum_or_join':
    out = '&{}'.format(decompile(tree.children[0]))
  elif tree.data == 'length':
    out = '#{}'.format(decompile(tree.children[0]))
  elif tree.data == 'selection':
    out = '@{}'.format(decompile(tree.children[0]))
  elif tree.data == 'minimum':
    out = '!<{}'.format(decompile(tree.children[0]))
  elif tree.data == 'maximum':
    out = '!>{}'.format(decompile(tree.children[0]))
  elif tree.data == 'flatten':
    out = '|{}'.format(decompile(tree.children[0]))
  elif tree.data == 'stats':
    out = '?{}'.format(decompile(tree.children[0]))
  elif tree.data == 'sort':
    out = '<>{}'.format(decompile(tree.children[0]))
  elif tree.data == 'shuffle':
    out = '><{}'.format(decompile(tree.children[0]))
  
  elif tree.data == 'slice':
    out = passthrough(tree.children)
  elif tree.data == 'whole_slice':
    out = '{indexable}[:]'.format(indexable=decompile(tree.children[0]))
  elif tree.data == 'start_slice':
    start_slice = '{indexable}[{start}:]'
    indexable, start = binop_decompile(tree.children)
    out = start_slice.format(indexable=indexable, start=start)
  elif tree.data == 'start_step_slice':
    start_step_slice = '{indexable}[{start}::{step}]'
    indexable, start, step = [decompile(child) for child in tree.children]
    out = start_step_slice.format(indexable=indexable, start=start, step=step)
  elif tree.data == 'start_stop_slice':
    start_stop_slice = '{indexable}[{start}:{stop}]'
    indexable, start, stop = [decompile(child) for child in tree.children]
    out = start_stop_slice.format(indexable=indexable, start=start, stop=stop)
  elif tree.data == 'fine_slice':
    fine_slice = '{indexable}[{start}:{stop}:{step}]'
    indexable, start, stop, step = [decompile(child) for child in tree.children]
    out = fine_slice.format(
      indexable=indexable,
      start=start,
      stop=stop,
      step=step)
  elif tree.data == 'stop_slice':
    stop_slice = '{indexable}[:{stop}]'
    indexable, stop = binop_decompile(tree.children)
    out = stop.slice.format(indexable=indexable, stop=stop)
  elif tree.data == 'stop_step_slice':
    stop_step_slice = '{indexable}[:{stop}:{step}]'
    indexable, stop, step = [decompile(child) for child in tree.children]
    out = stop_step_slice.format(indexable=indexable, stop=stop, step=step)
  elif tree.data == 'step_slice':
    step_slice = '{indexable}[::{step}]'
    indexable, step = binop_decompile(tree.children)
    out = step_slice.format(indexable=indexable, step=step)
  elif tree.data == 'not_a_slice':
    get_item = '{indexable}[index]'
    indexable, index = binop_decompile(tree.children)
    out = get_item.format(indexable=indexable, index=index)
  
  elif tree.data == 'application':
    out = passthrough(tree.children)
  elif tree.data == 'apply':
    apply_operation = '{left} -: {right}'
    left, right = binop_decompile(tree.children)
    out = apply_operation.format(left=left, right=right)
  
  elif tree.data == 'die':
    out = passthrough(tree.children)
  elif tree.data == 'scalar_die_all':
    scalar_all = '{dice} d {sides}'
    dice, sides = binop_decompile(tree.children)
    out = scalar_all.format(dice=dice, sides=sides)
  elif tree.data == 'scalar_die_highest':
    scalar_highest = '{dice} d {sides} h {keep}'
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = scalar_highest.format(dice=dice, sides=sides, keep=keep)
  elif tree.data == 'scalar_die_lowest':
    scalar_lowest = '{dice} d {sides} l {keep}'
    dice, sides, keep = [decompile(child) for child in tree.childen]
    out = scalar_lowest.format(dice=dice, sides=sides, keep=keep)
  elif tree.data == 'vector_die_all':
    vector_all = '{dice} r {sides}'
    dice, sides = binop_decompile(tree.children)
    out = vector_all.format(dice=dice, sides=sides)
  elif tree.data == 'vector_die_highest':
    vector_highest = '{dice} r {sides} h {keep}'
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = vector_highest.format(dice=dice, sides=sides, keep=keep)
  elif tree.data == 'vector_die_lowest':
    vector_lowest = '{dice} r {sides} l {keep}'
    dice, sides, keep = [decompile(child) for child in tree.children]
    out = vector_lowest.format(dice=dice, sides=sides, keep=keep)
  
  elif tree.data == 'plugin_op':
    out = passthrough(tree.children)
  elif tree.data == 'plugin_call':
    plugin_call = '{plugin_name} :: {plugin_operand}'
    name, operand = binop_decompile(tree.children)
    out = plugin_call.format(plugin_name=name, plugin_operand=operand)
  
  elif tree.data == 'call_or_atom':
    out = passthrough(tree.children)
  elif tree.data == 'function_call':
    function_call = '{callable_handle}({arguments})'
    handle = decompile(tree.children[0])
    arguments = ', '.join([decompile(child) for child in children[1:]])
    out = function_call.format(callable_handle=handle, arguments=arguments)
  
  elif tree.data == 'get_attribute':
    out = passthrough(tree.children)
  elif tree.data == 'getattr':
    get_attr = '{obj}.{identifier_chain}'
    obj = decompile(tree.children[0])
    chain = '.'.join([decompile(child) for child in children[1:]])
    out = get_attr.format(obj=obj, identifier_chain=chain)
  
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
    pop_list = '[{expression_chain}]'
    chain = ', '.join([decompile(child) for child in tree.children])
    out = pop_list.format(expression_chain=chain)
  elif tree.data == 'empty_list':
    out = '[]'
  elif tree.data == 'range_list':
    range_list = '[{start} to {stop}]'
    start, stop = binop_decompile(tree.children)
    out = range_list.format(start=start, stop=stop)
  elif tree.data == 'range_list_stepped':
    range_list_stepped = '[{start} to {stop} by {step}]'
    start, stop, step = [decompile(child) for child in tree.children]
    out = range_list_stepped.format(start=start, stop=stop, step=step)
  elif tree.data == 'dict_literal':
    out = passthrough(tree.children)
  elif tree.data == 'empty_dict':
    out = '{}'
  elif tree.data == 'populated_dict':
    pop_dict = '{ {key_value_pair_chain} }'
    chain = ', '.join([decompile(child) for child in tree.children])
    out = pop_dict.format(key_value_pair_chain=chain)
  elif tree.data == 'key_value_pair':
    kv_pair = '{key}: {value}'
    key, value = binop_decompile(tree.children)
    out = kv_pair.format(key=key, value=value)
  elif tree.data == 'identifier':
    out = passthrough(tree.children)
  elif tree.data == 'scoped_identifier':
    out = tree.children[0].value
  elif tree.data == 'private_identifier':
    out = 'my {}'.format(tree.children[-1].value)
  elif tree.data == 'server_identifier':
    out = 'our {}'.format(tree.children[-1].value)
  elif tree.data == 'global_identifier':
    out = 'global {}'.format(tree.children[-1].value)
  else:
    print('missed decompiling:', tree.data)
    out = '__UNIMPLEMENTED__: {}'.format(tree.data)
  
  return out







