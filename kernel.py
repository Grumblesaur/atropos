import lark
import handlers
import datastore
from undefined import Undefined

class OwnershipData:
  current_user   = ''
  current_server = ''
  
  def set(user, server):
    OwnershipData.current_user   = user
    OwnershipData.current_server = server

  def clear():
    OwnershipData.current_user   = ''
    OwnershipData.current_server = ''
  
  def get():
    return (OwnershipData.current_user, OwnershipData.current_server)


def handle_instruction(tree, user='', server=''):
  if tree.data == 'start':
    OwnershipData.set(user, server)
    out = handle_instruction(tree.children[0])
  
  elif tree.data == 'expression':
    out = handle_instruction(tree.children[0])
  
  elif tree.data == 'assignment':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'identifier_set':
    args = (tree.data, tree.children, *OwnershipData.get())
    out = handlers.handle_identifier_set(*args)
  elif tree.data == 'identifier_set_subscript':
    return handlers.handle_identifier_set_subscript(tree.data, tree.children)
    
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
  elif tree.data == 'string_literal':
    out = handlers.handle_string_literal(tree.children)
  elif tree.data == 'populated_dict':
    out = handlers.handle_dict_literal(tree.children)
  elif tree.data == 'empty_dict':
    out = handlers.handle_dict_literal(None)
  elif tree.data == 'identifier':
    out = handle_instruction(tree.children[0])
  elif tree.data in ['scoped_identifier', 'private_identifier', 'server_identifier']:
    args = (tree.data, tree.children, *OwnershipData.get())
    out = handlers.handle_identifiers(*args)
  elif tree.data == 'undefined_literal':
    out = Undefined
  elif tree.data == 'identifier_get':
    ident = handlers.handle_identifier_get(tree.children)
    if ident.private:
      out = datastore.private.get(ident.user, ident.name)
    elif ident.shared:
      out = datastore.server.get(ident.server, ident.name)
    elif ident.scoped:
      out = datastore.public.get(ident.name)
  
  elif tree.data == 'suffix':
    out = [handle_instruction(child) for child in tree.children]
    print(out)
    
  else:
    print(tree.data, tree.children)
    out = '__UNIMPLEMENTED__'
  
  if tree.data == 'start':
    OwnershipData.clear()
   
  return out


