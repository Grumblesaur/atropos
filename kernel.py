import lark
import handlers

def handle_instruction(tree):
  if tree.data == 'start':
    out = handle_instruction(tree.children[0])
  
  elif tree.data == 'expression':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'simple_assignment':
    print(tree.children)
    out = tree.data
  
  elif tree.data == 'bool_or':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_or':
    print(tree.children)
    out = tree.data
  
  elif tree.data == 'bool_xor':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_xor':
    print(tree.children)
    out = tree.data
  
  elif tree.data == 'bool_and':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_and':
    print(tree.children)
    out = tree.data
  
  elif tree.data == 'bool_not':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_not':
    print(tree.children)
    out = tree.data
  
  elif tree.data == 'comp':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'greater_than':
    out = handlers.handle_greater_than(tree.children)
  elif tree.data == 'greater_equal':
    out = handlers.handle_greater_equal(tree.children)
  elif tree.data == 'equal':
    out = handlers.handle_equal(tree.children)
  elif tree.data == 'not_equal':
    out = handlers.handle_not_equal(tree.children)
  elif tree.data == 'less_equal':
    out = handlers.handle_less_equal(tree.children)
  elif tree.data == 'less_than':
    out = handlers.handle_less_than(tree.children)
  
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
  elif tree.data == 'idempotence':
    out = handlers.handle_idempotence(tree.children)
  
  elif tree.data == 'power':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'exponent':
    out = handlers.handle_exponent(tree.children)
  elif tree.data == 'logarithm':
    out = handlers.handle_logarithm(tree.children)
  
  elif tree.data == 'die':
    out = handle_instruction(tree.children[0])
  elif 'scalar_die' in tree.data or 'vector_die' in tree.data:
    out = handlers.handle_dice(tree.data, tree.children)
  
  elif tree.data == 'atom':
    child = tree.children[0]
    out = handlers.handle_atom(child)
  elif tree.data == 'priority':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'populated_list':
    out = handlers.handle_list(tree.children)
  elif tree.data == 'empty_list':
    out = handlers.handle_list(None)
  else:
    print(tree.data)
    out = '__UNIMPLEMENTED__'
  
  return out


