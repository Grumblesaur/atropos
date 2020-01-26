import math
import rolls
import kernel
import datastore

class Identifier(object):
  def __init__(self, name, user, server):
    self.name    = name
    self.user    = user
    self.server  = server
    self.private = user is not None
    self.shared  = server is not None
    self.scoped  = user is None and server is None
  
  def __str__(self):
    return self.name

def binary_operation(children):
  out = []
  for child in children[:2]:
    out.append(kernel.handle_instruction(child))
  return tuple(out)

def handle_identifiers(data, children, user, server):
  ownership, _ = data.split('_')
  name = children[0].value
  if ownership == 'scoped':
    user, server = None, None
  elif ownership == 'shared':
    user = None
  elif ownership == 'private':
    server = None
  return Identifier(name, user, server)

def handle_identifier_set(data, children, user, server):
  ident = kernel.handle_instruction(children[0])
  value = kernel.handle_instruction(children[1])
  if ident.scoped:
    out = datastore.public.put(ident.name, value)
  elif ident.shared:
    out = datastore.server.put(server, ident.name, value)
  elif ident.private:
    out = datastore.private.put(user, ident.name, value)
  return out

def handle_identifier_set_subscript(data, children):
  value = kernel.handle_instruction(children.pop())
  ident = kernel.handle_instruction(children[0])
  subscripts = [kernel.handle_instruction(child) for child in children[1:]]
  if ident.private:
    target = datastore.private.get(ident.user, ident.name)
  elif ident.shared:
    target = datastore.server.get(ident.server, ident.name)
  elif ident.scoped:
    target = datastore.public.get(ident.name)
  
  subscripts = ''.join(['[{}]'.format(repr(subscript)) for subscript in subscripts])
  exec('target{ss} = {value}'.format(ss=subscripts, value=repr(value)))
  return value

def handle_subscript_assignment(data, children, user, server):
  inputs = '''  data = {}\n  children = {}\n  user = {}\n  server = {}'''.format(
    data, children, user, server
  )
  print('handle_subscript_assignment: {}'.format(inputs))
  return '__handle_subscript_assignment__'

def handle_logical_or(children):
  left, right = binary_operation(children)
  return left or right

def handle_logical_xor(children):
  left, right = binary_operation(children)
  return (left or right) and not (left and right)

def handle_logical_and(children):
  left, right = binary_operation(children)
  return left and right

def handle_logical_not(children):
  return not bool(kernel.handle_instruction(children[0]))

def handle_greater_than(children):
  left, right = binary_operation(children)
  return left > right

def handle_greater_equal(children):
  left, right = binary_operation(children)
  return left >= right

def handle_equal(children):
  left, right = binary_operation(children)
  return left == right

def handle_not_equal(children):
  left, right = binary_operation(children)
  return left != right

def handle_less_equal(children):
  left, right = binary_operation(children)
  return left <= right

def handle_less_than(children):
  left, right = binary_operation(children)
  return left < right 

def handle_left_shift(children):
  number, displacement = binary_operation(children)
  return number << displacement

def handle_right_shift(children):
  number, displacement = binary_operation(children)
  return number >> displacement

def handle_addition(children):
  augend, addend = binary_operation(children)
  return augend + addend

def handle_subtraction(children):
  minuend, subtrahend = binary_operation(children)
  
  try:
    result = minuend - subtrahend
  except TypeError as e:
    result = minuend
    try:
      for x in subtrahend:
        if x in minuend:
          result.remove(x)
    except:
      raise e

  return result

def handle_catenation(children):
  numbers = binary_operation(children)
  intstrings = map(lambda x: str(int(x)), numbers)
  return int(''.join(intstrings))

def handle_multiplication(children):
  multiplier, multiplicand = binary_operation(children)
  return multiplier * multiplicand

def handle_division(children):
  dividend, divisor = binary_operation(children)
  return dividend / divisor

def handle_remainder(children):
  dividend, divisor = binary_operation(children)
  return dividend % divisor

def handle_floor_division(children):
  dividend, divisor = binary_operation(children)
  return dividend // divisor

def handle_negation(children):
  return -kernel.handle_instruction(children[0])

def handle_idempotence(children):
  return kernel.handle_instruction(children[0])

def handle_exponent(children):
  mantissa, exponent = binary_operation(children)
  return mantissa ** exponent

def handle_logarithm(children):
  base, antilogarithm = binary_operation(children)
  return math.log(antilogarithm, base)

def handle_dice(node_type, children):
  result_type, _, keep_mode = node_type.split('_')
  dice   = kernel.handle_instruction(children[0])
  sides  = kernel.handle_instruction(children[1])
  count  = kernel.handle_instruction(children[2]) if len(children) > 2 else None
  as_sum = result_type == 'scalar'
  return rolls.kernel(dice, sides, count, mode=keep_mode, return_sum=as_sum) 

def handle_subscript_access(children):
  indexee  = kernel.handle_instruction(children[0])
  indexors = children[1:]
  for indexor in indexors:
    index = kernel.handle_instruction(indexor)
    indexee = indexee[index]
  return indexee

def handle_list_literal(children):
  items = [ ]
  if children:
    for child in children:
      items.append(kernel.handle_instruction(child))
  return items

def handle_dict_literal(children):
  pairs = { }
  if children:
    for child in children:
      key, value = binary_operation(child.children)
      pairs[key] = value
  return pairs

def handle_identifier_get(children):
  first = children[0].children[0]
  usr, svr = kernel.OwnershipData.get()
  if first.data == 'scoped_identifier':
    out = (first.children[0].value, None, None)
  elif first.data == 'private_identifier':
    out = (first.children[0].value, usr, None)
  elif first.data == 'server_identifier':
    out = (first.children[0].value, None, svr)
  return Identifier(*out)

def handle_number_literal(children):
  child = children.pop()
  try:
    x = int(child.value)
    f = float(child.value)
  except ValueError:
    x = None
    f = float(child.value)
  out = x if x == f else f
  return out

def handle_string_literal(children):
  return eval(children.pop().value)

def handle_boolean_literal(children):
  return eval(children.pop().value)


