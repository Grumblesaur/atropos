import math
import util
import kernel
import datastore
from collections.abc import Iterable
from undefined import Undefined
from identifier import Identifier
from function import Function
from function import FunctionCallException

def binary_operation(children):
  '''Internal function. Evaluates the first two elements
  of a list of lark Tree objects and returns the results
  as a tuple. Meant to be used with binary operations.'''
  out = []
  for child in children[:2]:
    out.append(kernel.handle_instruction(child))
  return tuple(out)

def handle_function(children):
  '''Produces a function object from the function syntax
  and returns that function object to be called later.'''
  code = children[-1]
  params = [child.value for child in children[:-1]]
  out = Function(code, *params)
  return out

def handle_function_call(children, scoping_data):
  '''Attempts to call the evaluated first element as a function,
  with all following elements as arguments. Scoping data is passed
  to push the function's parameters on the call stack. If the first
  element isn't a function, this is going to blow up.'''
  function = kernel.handle_instruction(children[0])
  arguments = map(kernel.handle_instruction, children[1:])
  return function(scoping_data, *arguments)

def handle_for_loop(children, scoping_data):
  iterator    = kernel.handle_instruction(children[0])
  iterable    = kernel.handle_instruction(children[1])
  name, start = iterator.name, iterable[0] if len(iterable) else None
  if start is None:
    finished = False
  else:
    scoping_data.push_scope()
    for element in iterable:
      scoping_data.get_scope()[name] = element
      kernel.handle_instruction(children[2])
    scoping_data.pop_scope()
    finished = True
  return finished

def handle_while_loop(children, scoping_data):
  scoping_data.push_scope()
  executed = 0
  while kernel.handle_instruction(children[0]):
    kernel.handle_instruction(children[1])
    executed += 1
  scoping_data.pop_scope()
  return executed

def handle_do_while_loop(children, scoping_data):
  scoping_data.push_scope()
  executed = 1
  kernel.handle_instruction(children[0])
  while kernel.handle_instruction(children[1]):
    kernel.handle_instruction(children[0])
    executed += 1
  scoping_data.pop_scope()
  return executed

def handle_if(children, scoping_data):
  executed = Undefined
  scoping_data.push_scope()
  if kernel.handle_instruction(children[0]):
    executed = kernel.handle_instruction(children[1])
  scoping_data.pop_scope()
  return executed

def handle_if_else(children, scoping_data):
  scoping_data.push_scope()
  if kernel.handle_instruction(children[0]):
    out = kernel.handle_instruction(children[1])
  else:
    out = kernel.handle_instruction(children[2])
  return out

def handle_short_body(children, scoping_data):
  scoping_data.push_scope()
  out = kernel.handle_instruction(children[0])
  scoping_data.pop_scope()
  return out

def handle_block(children, scoping_data):
  scoping_data.push_scope()
  tail = children[-1]
  for child in children[:-1]:
    kernel.handle_instruction(child)
  out = kernel.handle_instruction(tail)
  scoping_data.pop_scope()
  return out

def handle_identifiers(tree_data, children, scoping_data):
  '''Passes an Identifier object back to the interpreter
  when an identifier token is reached.'''
  ownership, _ = tree_data.split('_')
  name = children[0].value
  out = Identifier(name, scoping_data, ownership)
  return out

def handle_delete_variable(children):
  '''When a delete_variable production is reached,
  the identifier is removed from the datastore it
  belongs, possibly in accordance with a user or a
  server.'''
  ident = kernel.handle_instruction(children[0])
  out = ident.drop()
  return out

def handle_delete_element(children):
  '''When a delete_element production is reached,
  the subscripted object is removed from the containing
  iterable, which is possibly nested. This allows for an
  arbitrary level of nesting.'''
  ident = kernel.handle_instruction(children[0])
  subscripts = [kernel.handle_instruction(child) for child in children[1:]]
  subscripts = ''.join(['[{}]'.format(repr(s)) for s in subscripts])
  target = ident.get()
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
  return ident.put(value)

def handle_identifier_set_subscript(children):
  '''This handles when a subscripted element of a variable is
  assigned a value, or when such an element is created.'''
  value = kernel.handle_instruction(children[-1])
  ident = kernel.handle_instruction(children[0])
  subscripts = [kernel.handle_instruction(child) for child in children[1:-1]]
  subscripts = ''.join(['[{}]'.format(repr(subscript)) for subscript in subscripts])
  target = ident.get()
  exec('target{ss} = {value}'.format(ss=subscripts, value=repr(value)))
  return value

def handle_inline_if(children):
  condition = kernel.handle_instruction(children[1])
  if condition:
    out = kernel.handle_instruction(children[0])
  else:
    out = kernel.handle_instruction(children[2])
  return out

def handle_inline_if_binary(children):
  condition = kernel.handle_instruction(children[0])
  if condition:
    out = condition
  else:
    out = kernel.handle_instruction(children[1])
  return out

def handle_repetition(children):
  times = kernel.handle_instruction(children[1])
  out = [ ]
  for time in range(times):
    out.append(kernel.handle_instruction(children[0]))
  return out

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

def handle_comp_math(children):
  out = False
  comparisons = [kernel.handle_instruction(child) for child in children]
  operations = {
    '==' : lambda l, r: l == r,
    '!=' : lambda l, r: l != r,
    '>=' : lambda l, r: l >= r,
    '<=' : lambda l, r: l <= r,
    '>'  : lambda l, r: l > r,
    '<'  : lambda l, r: l < r
  }
  for i in range(0, len(children)-2, 2):
    left, op, right = comparisons[i:i+3]
    if not operations[op](left, right):
      break
  else:
    out = True
  return out

def handle_comp_obj(children):
  out = False
  comparisons = [kernel.handle_instruction(child) for child in children]
  operations = {'is' : lambda l, r: l is r, 'is not' : lambda l, r: l is not r}
  for i in range(0, len(children)-2, 2):
    left, op, right = comparisons[i:i+3]
    if not operations[op](left, right):
      break
  else:
    out = True
  return out

def handle_present(children, negate=False):
  element, collection = binary_operation(children)
  out = element in collection
  return out if not negate else not out

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
  '''Evaluates its operands and returns their product. If
  one operand is iterable and the other is integral, it returns
  the value of the iterable operand repeated a number of times
  equal to the integral operand.'''
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
  '''Evaluates its operand and returns the arithmetic inverse
  of the operand if the operand is less than 0.'''
  out = kernel.handle_instruction(children[0])
  return out if out >= 0 else -out

def handle_exponent(children):
  '''Evaluates its operands and returns the left operand
  raised to the power of the right operand.'''
  mantissa, exponent = binary_operation(children)
  return mantissa ** exponent

def handle_logarithm(children):
  '''Evaluates its operands and returns logarithm of
  the right operand in the base specified by the left operand.'''
  base, antilogarithm = binary_operation(children)
  return math.log(antilogarithm, base)

def handle_sum_or_join(children):
  operand = kernel.handle_instruction(children[0])
  if isinstance(operand, Iterable) and operand:
    out = operand[0]
    for element in operand[1:]:
      out += element
  elif isinstance(operand, Iterable) and not operand:
    out = 0
  else:
    out = operand
  return out

def handle_length(children):
  operand = kernel.handle_instruction(children[0])
  if isinstance(operand, Iterable):
    out = len(operand)
  elif isinstance(operand, Function):
    out = len(operand.params)
  else:
    out = 0
  return out

def handle_average(children):
  operand = kernel.handle_instruction(children[0])
  if isinstance(operand, (float, int)):
    operand = [operand]
  elif isinstance(operand, dict):
    operand = operand.values()
  return sum(operand) / len(operand)

def handle_extrema(children, min_or_max):
  operand = kernel.handle_instruction(children[0])
  if not isinstance(operand, Iterable):
    operand = [operand]
  return min(operand) if min_or_max == 'minimum' else max(operand)

def handle_flatten(children):
  operand = kernel.handle_instruction(children[0])
  return util.flatten(operand)

def handle_dice(node_type, children):
  '''Evaluates its operands and generates a random number
  in a manner akin to rolling dice:
    two-operand rolls have dice and sides
    three-operand rolls have dice, sides, and count
    
    dice: the number of dice to roll
    sides: the number of sides each die has (numbered from 1 to `sides`)
    count: the number of rolls kept for the final result
    
    all keep mode will keep all the rolls in the result list (2-op)
    high keep mode will keep the highest `count` rolls in the result list (3-op)
    low keep mode will keep the lowest `count` rolls in the result list (3-op)
    
    scalar result types will sum the output of the die roll.
    vector result types will return the list of components of the die roll.
  '''
  result_type, _, keep_mode = node_type.split('_')
  dice   = kernel.handle_instruction(children[0])
  sides  = kernel.handle_instruction(children[1])
  count  = kernel.handle_instruction(children[2]) if len(children) > 2 else None
  as_sum = result_type == 'scalar'
  return util.roll(dice, sides, count, mode=keep_mode, return_sum=as_sum) 

def handle_slices(slice_type, children):
  v = kernel.handle_instruction(children[0])
  slice_args = [kernel.handle_instruction(child) for child in children[1:]]
  if slice_type == 'whole_slice':
    out = v[:]
  elif slice_type == 'start_slice':
    out = v[slice_args[0]:]
  elif slice_type == 'start_step_slice':
    out = v[slice_args[0]::slice_args[1]]
  elif slice_type == 'start_stop_slice':
    out = v[slice_args[0]:slice_args[1]]
  elif slice_type == 'fine_slice':
    out = v[slice_args[0]:slice_args[1]:slice_args[2]]
  elif slice_type == 'stop_slice':
    out = v[:slice_args[0]]
  elif slice_type == 'stop_step_slice':
    out = v[:slice_args[0]:slice_args[1]]
  elif slice_type == 'step_slice':
    out = v[::slice_args[0]]
  elif slice_type == 'not_a_slice':
    out = handle_subscript_access(children)
  return out

def handle_subscript_access(children):
  '''Evaluates its operands, and iteratively indexes/subscripts the
  first operand with the rest of the operands from left to right.'''
  iterable, index = binary_operation(children)
  return iterable[index]

def handle_list_literal(children):
  '''Evaluates its components and inserts them into a list,
  then returns that list.'''
  items = [ ]
  if children:
    for child in children:
      items.append(kernel.handle_instruction(child))
  return items

def handle_list_range_literal(children):
  '''Constructs and returns list of numbers in a linear order. For two
  arguments, the resulting list will consist of all integers in the half-
  open interval from the value of the first argument to the second argument.
  For three arguments, the third argument specifies a skip interval.'''
  args = [kernel.handle_instruction(child) for child in children]
  return [x for x in range(*args)]

def handle_dict_literal(children):
  '''Evaluates its components and constructs a hash table of
  key-value pairs, then returns that hash table.'''
  pairs = { }
  if children:
    for child in children:
      key, value = binary_operation(child.children)
      pairs[key] = value
  return pairs

def handle_number_literal(children):
  '''Evaluates a numeric literal and returns an integer if the floating point
  result and integer result are the same, else returns a floating point value.'''
  child = children[-1]
  try:
    x = int(child.value)
    f = float(child.value)
  except ValueError:
    x = None
    f = float(child.value)
  out = x if x == f else f
  return out

def handle_string_literal(children):
  '''Evaluates a string literal and returns a string.'''
  return eval(children[-1].value)

def handle_boolean_literal(children):
  '''Evaluates a boolean literal and returns a boolean.'''
  return eval(children[-1].value)


