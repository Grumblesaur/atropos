import lark
from . import handlers
from . import datastore
from . import ownership
from .undefined import Undefined

scoping_data = None
identifier_types = (
  'scoped_identifier',
  'private_identifier',
  'server_identifier',
  'global_identifier')

class LoopBreak(Exception):
  pass

def handle_instruction(tree, user='', server=''):
  global scoping_data
  if tree.data == 'start':
    scoping_data = ownership.ScopingData(user, server)
    out = [handle_instruction(child) for child in tree.children][-1]
  
  elif tree.data == 'block':
    out = handlers.handle_block(tree.children, scoping_data)
  elif tree.data == 'short_body':
    out = handlers.handle_block(tree.children, scoping_data)  
  elif tree.data == 'function':
    out = handlers.handle_function(tree.children)
  
  elif tree.data == 'function_call':
    out = handlers.handle_function_call(tree.children, scoping_data)
  
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
  
  elif tree.data == 'access':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'subscript_access':
    out = handlers.handle_subscript_access(tree.children)
  
  elif tree.data == 'die':
    out = handle_instruction(tree.children[0])
  elif 'scalar_die' in tree.data or 'vector_die' in tree.data:
    out = handlers.handle_dice(tree.data, tree.children)
  
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
    out = handlers.handle_identifiers(tree.data, tree.children, scoping_data)
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
   
  return out


