import math
import rolls
import kernel
import datastore

class Identifier(object):
  '''Internal class for storing the information of
  an identifier prior to its evaluation.'''
  
  def __init__(self, name, user, server):
    '''Creates an Identifier object.
      name: the name of this identifier.
      user: if this identifier is associated with a person, this is their name.
      server: if this identifier is associated with a server, this is its name.'''
    self.name    = name
    self.user    = user
    self.server  = server
    self.private = user is not None
    self.shared  = server is not None
    self.scoped  = user is None and server is None
  
  def __repr__(self):
    '''eval-able string representation of an Identifier.'''
    return 'Identifier({n}, {u}, {s})'.format(
      n=repr(self.name),
      u=repr(self.user),
      s=repr(self.server))
  
  def __str__(self):
    return self.name


def binary_operation(children):
  '''Internal function. Evaluates the first two elements
  of a list of lark Tree objects and returns the results
  as a tuple. Meant to be used with binary operations.'''
  out = []
  for child in children[:2]:
    out.append(kernel.handle_instruction(child))
  return tuple(out)

def handle_identifiers(data, children, user, server):
  '''Passes an Identifier object back to the interpreter
  when an identifier token is reached.'''
  ownership, _ = data.split('_')
  name = children[0].value
  if ownership == 'scoped':
    args = (name, None, None)
  elif ownership == 'server':
    args = (name, None, server)
  elif ownership == 'private':
    args = (name, user, None)
  out = Identifier(*args)
  return out

def handle_delete_variable(children):
  '''When a delete_variable production is reached,
  the identifier is removed from the datastore it
  belongs, possibly in accordance with a user or a
  server.'''
  ident = kernel.handle_instruction(children[0])
  if ident.private:
    out = datastore.private.drop(ident.user, ident.name)
  elif ident.shared:
    out = datastore.shared.drop(ident.server, ident.name)
  elif ident.scoped:
    out = datastore.public.drop(ident.name)
  return out

def handle_delete_element(children):
  '''When a delete_element production is reached,
  the subscripted object is removed from the containing
  iterable, which is possibly nested. This allows for an
  arbitrary level of nesting.'''
  ident = kernel.handle_instruction(children[0])
  subscripts = [kernel.handle_instruction(child) for child in children[1:]]
  subscripts = ''.join(['[{}]'.format(repr(s)) for s in subscripts])
  if ident.private:
    target = datastore.private.get(ident.user, ident.name)
  elif ident.shared:
    target = datastore.server.get(ident.server, ident.name)
  elif ident.scoped:
    target = datastore.public.get(ident.name)
  val_repr = 'target{ss}'.format(ss=subscripts)
  out = eval(val_repr)
  exec('del {}'.format(val_repr))
  return out

def handle_identifier_set(children):
  '''This handles when an identifier is assigned a value,
  which is also when an identifier is created. The
  identifier is added to the appropriate datastore.'''
  ident = kernel.handle_instruction(children[0])
  value = kernel.handle_instruction(children[1])
  if ident.scoped:
    out = datastore.public.put(ident.name, value)
  elif ident.shared:
    out = datastore.server.put(ident.server, ident.name, value)
  elif ident.private:
    out = datastore.private.put(ident.user, ident.name, value)
  return out

def handle_identifier_set_subscript(children):
  '''This handles when a subscripted element of a variable is
  assigned a value, or when such an element is created.'''
  value = kernel.handle_instruction(children.pop())
  ident = kernel.handle_instruction(children[0])
  subscripts = [kernel.handle_instruction(child) for child in children[1:]]
  subscripts = ''.join(['[{}]'.format(repr(subscript)) for subscript in subscripts])
  if ident.private:
    target = datastore.private.get(ident.user, ident.name)
  elif ident.shared:
    target = datastore.server.get(ident.server, ident.name)
  elif ident.scoped:
    target = datastore.public.get(ident.name)
  
  exec('target{ss} = {value}'.format(ss=subscripts, value=repr(value)))
  return value

def handle_logical_or(children):
  '''Evaluate operands and return their logical disjunction.'''
  left, right = binary_operation(children)
  return left or right

def handle_logical_xor(children):
  '''Evaluate operands, then return them according to
  a boolean interpretation of xor. This is *not* a
  bitwise operator.'''
  left, right = binary_operation(children)
  return (left or right) and not (left and right)

def handle_logical_and(children):
  '''Evaluate operands and return their logical conjunction.'''
  left, right = binary_operation(children)
  return left and right

def handle_logical_not(children):
  '''Evaluate operand and return the inverse of its boolean conversion.'''
  return not bool(kernel.handle_instruction(children[0]))

def handle_greater_than(children):
  '''Evaluate operands and return True if left > right else False.'''
  left, right = binary_operation(children)
  return left > right

def handle_greater_equal(children):
  '''Evaluate operands and return True if left >= right else False.'''
  left, right = binary_operation(children)
  return left >= right

def handle_equal(children):
  '''Evaluate operands and return True if they are equal else False.'''
  left, right = binary_operation(children)
  return left == right

def handle_not_equal(children):
  '''Evaluate operands and return True if they are inequal else False.'''
  left, right = binary_operation(children)
  return left != right

def handle_less_equal(children):
  '''Evaluate operands and return True if left <= right else False.'''
  left, right = binary_operation(children)
  return left <= right

def handle_less_than(children):
  '''Evaluate operands and return True if left < right else False.'''
  left, right = binary_operation(children)
  return left < right 

def handle_left_shift(children):
  '''Evaluate operands and bitwise shift the left operand
  towards its big end by the value of the right operand,
  then return that value.'''
  number, displacement = binary_operation(children)
  return number << displacement

def handle_right_shift(children):
  '''Evaluate operands and bitwise shift the left operand
  towards its little end by the value of the right operand,
  then return that value.'''
  number, displacement = binary_operation(children)
  return number >> displacement

def handle_addition(children):
  '''Evaluates its operands and returns their sum. For
  strings, this concatenates from left to right.'''
  augend, addend = binary_operation(children)
  return augend + addend

def handle_subtraction(children):
  '''Evaluates its operands and returns their difference,
  from left to right. For iterables, this acts as set
  subtraction, where all values present in the right operand
  will be removed from the left operand, and the resulting
  new iterable is returned.'''
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
  '''Evaluates its operands, which are expected to be numeric,
  truncates them to integers, and then converts them to strings.
  The strings are then concatenated from left to right, converted
  back to one combined integer, and returned.'''
  numbers = binary_operation(children)
  intstrings = map(lambda x: str(int(x)), numbers)
  return int(''.join(intstrings))

def handle_multiplication(children):
  '''Evaluates its operands and returns their product.'''
  multiplier, multiplicand = binary_operation(children)
  return multiplier * multiplicand

def handle_division(children):
  '''Evaluates its operands and returns the quotient of
  the left operand divided by the right operand.'''
  dividend, divisor = binary_operation(children)
  return dividend / divisor

def handle_remainder(children):
  '''Evaluates its operands and returns the remainder of
  the left operand divided by the right operand.'''
  dividend, divisor = binary_operation(children)
  return dividend % divisor

def handle_floor_division(children):
  '''Evaluates its operands and returns the quotient
  of the left operand divided by the right operand,
  rounded down to the nearest integer.'''
  dividend, divisor = binary_operation(children)
  return dividend // divisor

def handle_negation(children):
  '''Evaluates its operand and returns its arithmetic inverse.'''
  return -kernel.handle_instruction(children[0])

def handle_absolute_value(children):
  out = kernel.handle_instruction(children[0])
  return out if out >= 0 else -out

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

def handle_list_range_literal(children):
  args = [kernel.handle_instruction(child) for child in children]
  return [x for x in range(*args)]

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


