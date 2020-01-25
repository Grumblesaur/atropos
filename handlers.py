import math
import rolls
import kernel

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

def handle_simple_assignment(data, children, user, server):
  return '__{}__'.format(data)

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
  return minuend - subtrahend

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

def handle_list(children):
  items = [ ]
  if children:
    for child in children:
      items.append(kernel.handle_instruction(child))
  return items

def handle_identifiers(children):
  first = children[0]
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

def handle_boolean_literal(children):
  return eval(children.pop().value)


