import copy
import math
import random
import re
import statistics
import time
from collections.abc import Iterable

from dicelang import plugins
from dicelang import util
from dicelang.function import Function
from dicelang.identifier import Identifier
from dicelang.ownership import ScopingData
from dicelang.undefined import Undefined

class Visitor(object):
  def __init__(self, public_data, server_data, private_data, core_data, timeout=12):
    self.public = public_data
    self.shared = server_data
    self.private = private_data
    self.core = core_data
    self.scoping_data = None
    self.user = None
    self.server = None
    self.loop_timeout = timeout
    self.depth = 0
    
  def walk(self, parse_tree, user_id, server_id, scoping_data=None):
    if scoping_data is None:
      self.scoping_data = ScopingData(user_id, server_id)
    else:
      self.scoping_data = scoping_data
    self.depth += 1
    out = self.handle_instruction(parse_tree)
    self.depth -= 1
    
    # Reentrancy case -- when a dicelang Function is executed,
    # we don't want to erase our scoping data since we're still
    # pushing and popping stack frames. When depth is zero, we
    # are finished executing.
    if not self.depth:
      self.scoping_data = None
    return out
  
  def process_operands(self, children):
    return [self.handle_instruction(c) for c in children]
  
  def handle_instruction(self, tree):
    if tree.data == 'start':
      out = [self.handle_instruction(c) for c in tree.children][-1]
    elif tree.data == 'block' or tree.data == 'short_body':
      out = self.handle_block(tree.children)
    elif tree.data == 'function':
      out = self.handle_function(tree.children)
    
    elif tree.data == 'for_loop':
      out = self.handle_for_loop(tree.children)
    elif tree.data == 'while_loop':
      out = self.handle_while_loop(tree.children)
    elif tree.data == 'do_while_loop':
      out = self.handle_do_while_loop(tree.children)
    elif tree.data == 'conditional':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'if':
      out = self.handle_if(tree.children)
    elif tree.data == 'if_else':
      out = self.handle_if_else(tree.children)
    
    elif tree.data == 'expression':
      out = self.handle_instruction(tree.children[0])
    
    elif tree.data == 'import':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'standard_import':
      out = self.handle_standard_import(tree.children)
    elif tree.data == 'as_import':
      out = self.handle_as_import(tree.children)
    
    elif tree.data == 'deletion':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'delete_variable':
      out = self.handle_delete_variable(tree.children)
    elif tree.data == 'delete_element':
      out = self.handle_delete_element(tree.children)
    elif tree.data == 'delete_attribute':
      out = self.handle_delete_attribute(tree.children)
    
    elif tree.data == 'assignment':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'identifier_set':
      out = self.handle_identifier_set(tree.children)
    elif tree.data == 'identifier_set_subscript':
      out = self.handle_identifier_set_subscript(tree.children)
    elif tree.data == 'setattr':
      out = self.handle_setattr(tree.children)
    
    elif tree.data == 'if_expr':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'inline_if':
      out = self.handle_inline_if(tree.children)
    elif tree.data == 'inline_if_binary':
      out = self.handle_inline_if_binary(tree.children)
    elif tree.data == 'repeat':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'repetition':
      out = self.handle_repetition(tree.children)
    
    elif tree.data == 'bool_or':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'logical_or':
      out = self.handle_logical_or(tree.children)
    elif tree.data == 'bool_xor':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'logical_xor':
      out = self.handle_logical_xor(tree.children)
    elif tree.data == 'bool_and':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'logical_and':
      out = self.handle_logical_and(tree.children)
    elif tree.data == 'bool_not':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'logical_not':
      out = self.handle_logical_not(tree.children)
    
    elif tree.data == 'comp':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'comp_math':
      out = self.handle_comp_math(tree.children)
    elif tree.data == 'comp_obj':
      out = self.handle_comp_obj(tree.children)
    elif tree.data == 'math_comp':
      out = tree.children[0].value
    elif tree.data == 'obj_comp':
      out = 'is' if len(tree.children) == 1 else 'is not'
    elif tree.data == 'present':
      out = self.handle_present(tree.children)
    elif tree.data == 'absent':
      out = self.handle_present(tree.children, negate=True)
    
    elif tree.data == 'shift':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'left_shift':
      out = self.handle_left_shift(tree.children)
    elif tree.data == 'right_shift':
      out = self.handle_right_shift(tree.children)
    
    elif tree.data == 'arithm':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'addition':
      out = self.handle_addition(tree.children)
    elif tree.data == 'subtraction':
      out = self.handle_subtraction(tree.children)
    elif tree.data == 'catenation':
      out = self.handle_catenation(tree.children)
    
    elif tree.data == 'term':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'multiplication':
      out = self.handle_multiplication(tree.children)
    elif tree.data == 'division':
      out = self.handle_division(tree.children)
    elif tree.data == 'remainder':
      out = self.handle_remainder(tree.children)
    elif tree.data == 'floor_division':
      out = self.handle_floor_division(tree.children)
    
    elif tree.data == 'factor':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'negation':
      out = self.handle_negation(tree.children)
    elif tree.data == 'absolute_value':
      out = self.handle_absolute_value(tree.children)
    
    elif tree.data == 'power':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'exponent':
      out = self.handle_exponent(tree.children)
    elif tree.data == 'logarithm':
      out = self.handle_logarithm(tree.children)
    
    elif tree.data == 'reduction':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'sum_or_join':
      out = self.handle_sum_or_join(tree.children)
    elif tree.data == 'length':
      out = self.handle_length(tree.children)
    elif tree.data == 'selection':
      out = self.handle_selection(tree.children)
    elif tree.data in ('minimum', 'maximum'):
      out = self.handle_extrema(tree.children, tree.data)
    elif tree.data == 'flatten':
      out = self.handle_flatten(tree.children)
    elif tree.data == 'stats':
      out = self.handle_stats(tree.children)
    elif tree.data == 'sort':
      out = self.handle_sort(tree.children)
    elif tree.data == 'shuffle':
      out = self.handle_shuffle(tree.children)
    
    elif tree.data == 'slice':
      out = self.handle_instruction(tree.children[0])
    elif '_slice' in tree.data:
      out = self.handle_slices(tree.data, tree.children)
    
    elif tree.data == 'plugin_op':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'plugin_call':
      out = self.handle_plugin_call(tree.children)
    
    elif tree.data == 'die':
      out = self.handle_instruction(tree.children[0])
    elif 'vector_die' in tree.data or 'scalar_die' in tree.data:
      out = self.handle_dice(tree.data, tree.children)
    
    elif tree.data == 'application':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'apply':
      out = self.handle_apply(tree.children)

    elif tree.data == 'call_or_atom':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'function_call':
      out = self.handle_function_call(tree.children)
    
    elif tree.data == 'get_attribute':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'getattr':
      out = self.handle_getattr(tree.children)
    
    elif tree.data == 'regex':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'match':
      out = self.handle_match(tree.children)
    elif tree.data == 'search':
      out = self.handle_search(tree.children)
    
    elif tree.data == 'atom' or tree.data == 'priority':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'number_literal':
      out = self.handle_number_literal(tree.children)
    elif tree.data == 'boolean_literal':
      out = self.handle_boolean_literal(tree.children)
    elif tree.data == 'string_literal':
      out = self.handle_string_literal(tree.children)
    elif tree.data == 'populated_list':
      out = self.handle_list_literal(tree.children)
    elif tree.data == 'empty_list':
      out = self.handle_list_literal(None)
    elif tree.data == 'range_list' or tree.data == 'range_list_stepped':
      out = self.handle_list_range_literal(tree.children)
    elif tree.data == 'closed_list' or tree.data == 'closed_list_stepped':
      out = self.handle_closed_list_literal(tree.children)
    elif tree.data == 'populated_dict':
      out = self.handle_dict_literal(tree.children)
    elif tree.data == 'empty_dict':
      out = self.handle_dict_literal(None)
    elif tree.data == 'identifier':
      out = self.handle_instruction(tree.children[0])
    elif tree.data in ('core_identifier',
                       'scoped_identifier',
                       'global_identifier',
                       'server_identifier',
                       'private_identifier'):
      out = self.handle_identifiers(tree.data, tree.children)
    elif tree.data == 'undefined_literal':
      out = Undefined
    elif tree.data == 'identifier_get':
      ident = self.handle_instruction(tree.children[0])
      out = ident.get()
    else:
      print(tree.data, tree.children)
      out = f'__UNIMPLEMENTED__: {tree.data}'
    return out 
    
    
  def handle_block(self, children):
    self.scoping_data.push_scope()
    tail = children[-1]
    for child in children[:-1]:
      self.handle_instruction(child)
    out = self.handle_instruction(tail)
    self.scoping_data.pop_scope()
    return out
  
  def handle_function(self, children):
    '''Builds a function object.'''
    code = children[-1]
    params = [c.value for c in children[:-1]]
    out = Function(code, params)
    out.visitor = self
    return out

  def handle_for_loop(self, children):
    '''Executes a block or expression once for each element of its
    iterable. The iterator variable takes the value of each element
    in order, from first to last, changing each iteration. As the for-loop
    is an expression, its return value is a list containing the return value
    of the loop's code for each iteration,, or an empty list if the code did
    not execute. This list can be treated as a boolean.'''
    iterator = self.handle_instruction(children[0])
    iterable = self.handle_instruction(children[1])
    name = iterator.name
    if isinstance(iterable, dict):
      iterable = list(iterable.keys())
    
    start = iterable[0] if len(iterable) else None
    if start is None:
      results = [ ]
    else:
      results = [ ]
      self.scoping_data.push_scope()
      for element in iterable:
        self.scoping_data.get_scope()[name] = element
        results.append(self.handle_instruction(children[2]))
      self.scoping_data.pop_scope()
    return results
  
  def handle_while_loop(self, children):
    '''Executes a block or expression until or unless the conditional evaluates
    to a falsy value. As the while loop is itself an expression, it will return
    a list of the results of each of the loop's iterations.'''
    self.scoping_data.push_scope()
    results = [ ]
    timeout = time.time() + self.loop_timeout
    while self.handle_instruction(children[0]):
      results.append(self.handle_instruction(children[1]))
      if time.time() > timeout:
        times = len(results)
        e = f'`while` loop iterated {times} times without terminating.'
        raise LoopTimeout(e)
    self.scoping_data.pop_scope()
    return results

  def handle_do_while_loop(self, children):
    '''Same as a while loop, but is guaranteed to execute at least once.'''
    self.scoping_data.push_scope()
    results = [self.handle_instruction(children[0])]
    timeout = time.time() + self.loop_timeout
    while self.handle_instruction(children[1]):
      results.append(self.handle_instruction(children[0]))
      if time.time() > timeout:
        times = len(results)
        e = f'`do while` loop iterated {times} times without terminating.'
        raise LoopTimeout(e)
    self.scoping_data.pop_scope()
    return results

  def handle_if(self, children):
    '''Executes its code only if the conditional expression evaluates to
    a truthy value. Returns the code's result if truthy, otherwise it returns
    Undefined.'''
    result = Undefined
    self.scoping_data.push_scope()
    if self.handle_instruction(children[0]):
      result = self.handle_instruction(children[1])
    self.scoping_data.pop_scope()
    return result
  
  def handle_if_else(self, children):
    '''Similar to `if`, except the code of the else clause is evaluated and
    its value returned when the conditional expression is falsy, rather than
    only `Undefined`.'''
    self.scoping_data.push_scope()
    if self.handle_instruction(children[0]):
      out = self.handle_instruction(children[1])
    else:
      out = self.handle_instruction(children[2])
    self.scoping_data.pop_scope()
    return out
  
  def handle_standard_import(self, children):
    ident = self.handle_instruction(children[1])
    value = copy.deepcopy(ident.get())
    if value is not Undefined:
      imported = Identifier(
        ident.name,
        self.scoping_data,
        'server',
        self.public,
        self.shared,
        self.private,
        self.core)
      imported.put(value)
      out = True
    else:
      out = False
    return out
      
  
  def handle_as_import(self, children):
    importable, alias = [self.handle_instruction(c) for c in children[1:]]
    value = copy.deepcopy(importable.get())
    new_name = alias.name
    if value is not Undefined:
      imported = Identifier(
        new_name,
        self.scoping_data,
        alias.mode,
        self.public,
        self.shared,
        self.private,
        self.core)
      imported.put(value)
      out = True
    else:
      out = False
    return out
  
  def handle_delete_variable(self, children):
    ident = self.handle_instruction(children[0])
    return ident.drop()

  def handle_delete_element(self, children):
    '''Construct a Python code string that will delete from the possibly-
    nested dict object, and exec it to remove the key-value pair from the
    dict. The value is returned.'''
    ident = self.handle_instruction(children[0])
    subscripts = [self.handle_instruction(c) for c in children[1:]]
    subscripts = ''.join([f'[{s!r}]' for s in subscripts])
    target = ident.get()
    val_repr = f'target{subscripts}'
    Function.use_serializable_function_repr(True)
    out = eval(val_repr)
    exec(f'del {val_repr}')
    Function.use_serializable_function_repr(False)
    return out

  def handle_delete_attribute(self, children):
    '''Similar to delete element, but this results from a chain of `.`
    accesses, and not `[x]` indexes.'''
    ident = self.handle_instruction(children[0])
    subscripts = [self.handle_instruction(c) for c in children[1:]]
    subscripts = ''.join([f'[{id_.name!r}]' for id_ in subscripts])
    target = ident.get()
    val_repr = f'target{subscripts}'
    Function.use_serializable_function_repr(True)
    out = eval(val_repr)
    exec(f'del {val_repr}')
    Function.use_serializable_function_repr(False)
    return out

  def handle_identifier_set(self, children):
    ident = self.handle_instruction(children[0])
    value = self.handle_instruction(children[1])
    return ident.put(value)
  
  def handle_identifier_set_subscript(self, children):
    '''Handle the assignment of a value to an arbitrarily-chained subscript
    of a variable.'''
    value = self.handle_instruction(children[-1])
    ident = self.handle_instruction(children[0])
    subscripts = [self.handle_instruction(c) for c in children[1:-1]]
    for s in subscripts:
      if isinstance(s, Function):
        error = f'Functions cannot be used as keys or indices. ({s!r})'
        raise TypeError(error)
    subscripts = ''.join([f'[{s!r}]' for s in subscripts])
    target = ident.get()
    Function.use_serializable_function_repr(True)
    stmt = f'target{subscripts} = {value!r}'
    exec(stmt)
    Function.use_serializable_function_repr(False)
    return value

  def handle_setattr(self, children):
    '''Handle the assignment of a value to an arbitrarily-chained attribute
    of a variable.'''
    value = self.handle_instruction(children[-1])
    ident = self.handle_instruction(children[0])
    attr_chain = [self.handle_instruction(c) for c in children[1:-1]]
    subscripts = ''.join([f'[{attr.name!r}]' for attr in attr_chain])
    target = ident.get()
    Function.use_serializable_function_repr(True)
    stmt = f'target{subscripts} = {value!r}'
    exec(stmt)
    Function.use_serializable_function_repr(False)
    return value

  def handle_inline_if(self, children):
    '''Shorthand Python-like inline if-else expression.'''
    condition = self.handle_instruction(children[1])
    if condition:
      out = self.handle_instruction(children[0])
    else:
      out = self.handle_instruction(children[2])
    return out
  
  def handle_inline_if_binary(self, children):
    '''Akin to the inline_if, but there are only two operands, and the first
    is both the condition, and the return value if the condition is truthy.'''
    condition = self.handle_instruction(children[0])
    if condition:
      out = condition
    else:
      out = self.handle_instruction(children[1])
    return out

  def handle_repetition(self, children):
    '''For loop shorthand. Left side is an expression to be evaluated, right
    side is the number of times to evaluate it. Return value is a list
    containing the result of each evaluation of the left side.'''
    times = self.handle_instruction(children[1])
    out = [ ]
    for time in range(times):
      out.append(self.handle_instruction(children[0]))
    return out
    
  def handle_logical_or(self, children):
    left = self.handle_instruction(children[0])
    if left:
      out = left
    else:
      out = self.handle_instruction(children[1])
    return out
  
  def handle_logical_xor(self, children):
    left, right = self.process_operands(children)
    return (left or right) and not (left and right)
  
  def handle_logical_and(self, children):
    left = self.handle_instruction(children[0])
    if left:
      out = self.handle_instruction(children[1])
    else:
      out = left
    return out

  def handle_logical_not(self, children):
    operand = self.handle_instruction(children[-1])
    return not operand
  
  def handle_comp_math(self, children):
    '''Support sensible mathematical chained comparisons, like Python's.'''
    out = False
    operands_and_operators = self.process_operands(children)
    operations = {
      '==' : lambda l, r: l == r,
      '!=' : lambda l, r: l != r,
      '>=' : lambda l, r: l >= r,
      '<=' : lambda l, r: l <= r,
      '>'  : lambda l, r: l  > r,
      '<'  : lambda l, r: l  < r
    }
    for i in range(0, len(operands_and_operators)-2, 2):
      left, op, right = operands_and_operators[i:i+3]
      if not operations[op](left, right):
        break
    else:
      out = True
    return out

  def handle_comp_obj(self, children):
    '''Similar to comp_math, but handles only identity comparison.'''
    out = False
    operands_and_operators = self.process_operands(children)
    operations = {'is': lambda l, r: l is r, 'is not': lambda l, r: l is not r}
    for i in range(0, len(operands_and_operators)-2, 2):
      left, op, right = operands_and_operators[i:i+3]
      if not operations[op](left, right):
        break
    else:
      out = True
    return out

  def handle_present(self, children, negate=False):
    '''Membership check of left in right.'''
    element, container = self.process_operands(children)
    out = element in container
    return out if not negate else not out

  def handle_left_shift(self, children):
    return util.shift(*self.process_operands(children))
  
  def handle_right_shift(self, children):
    return util.shift(*self.process_operands(children), left_shift=False)
  
  def handle_addition(self, children):
    operands = self.process_operands(children)
    return util.addition(*operands)
  
  def handle_subtraction(self, children):
    '''Normal subtraction, as well as list element/dict key removal.'''
    minuend, subtrahend = self.process_operands(children)
    try:
      result = minuend - subtrahend
    except TypeError as e:
      result = minuend[:]
      try:
        for x in subtrahend:
          if x in minuend:
            result.remove(x)
      except:
        raise e
    return result

  def handle_catenation(self, children):  
    numbers = self.process_operands(children)
    intstrings = map(lambda x: str(int(x)), numbers)
    return int(''.join(intstrings))

  def handle_multiplication(self, children):
    multiplier, multiplicand = self.process_operands(children)
    array = (list, str)
    numeric = (int, float)
    if isinstance(multiplier, array) and isinstance(multiplicand, numeric):
      out = util.iterable_repetition(multiplier, multiplicand)
    elif isinstance(multiplier, numeric) and isinstance(multiplicand, array):
      out = util.iterable_repetition(multiplicand, multiplier)
    else:
      out = multiplier * multiplicand
    return out

  def handle_division(self, children):
    dividend, divisor = self.process_operands(children)
    return dividend / divisor
  
  def handle_remainder(self, children):
    dividend, divisor = self.process_operands(children)
    return dividend % divisor
  
  def handle_floor_division(self, children):
    dividend, divisor = self.process_operands(children)
    return dividend // divisor
  
  def handle_negation(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, (list, str)):
      out = operand[::-1]
    else:
      out = -operand
    return out
  
  def handle_absolute_value(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, (float, int)):
      out = operand if operand >= 0 else -operand
    else:
      out = operand
    return out
    
  def handle_exponent(self, children):
    mantissa, exponent = self.process_operands(children)
    util.log(f'{mantissa} ** {exponent}')
    return mantissa ** exponent
  
  def handle_logarithm(self, children):
    base, exponent = self.process_operands(children)
    return math.log(exponent, base)

  def handle_sum_or_join(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, Iterable) and operand:
      out = operand[0]
      for element in operand[1:]:
        out += element
    elif isinstance(operand, Iterable) and not operand:
      out = 0
    else:
      out = operand
    return out

  def handle_length(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, Iterable):
      out = len(operand)
    elif isinstance(operand, Function):
      out = len(operand.params)
    else:
      out = 0
    return out
  
  def handle_selection(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, (float, int)):
      operand = [operand]
    elif isinstance(operand, dict):
      operand = [[key, value] for key, value in operand.items()]
    return random.choice(operand)

  def handle_extrema(self, children, extremum_type):
    operand = self.process_operands(children)[0]
    if not isinstance(operand, Iterable):
      operand = [operand]
    return min(operand) if extremum_type == 'minimum' else max(operand)
  
  def handle_flatten(self, children):
    return util.flatten(self.process_operands(children)[0])
  
  def handle_stats(self, children):
    operand = self.process_operands(children)[0]
    out = { }
    if isinstance(operand, (float, int)):
      operand = [operand]
    elif isinstance(operand, dict):
      operand = operand.values()
    out['average'] = statistics.mean(operand)
    out['minimum'] = min(operand)
    out['median' ] = statistics.median(operand)
    out['maximum'] = max(operand)
    out['size'   ] = len(operand)
    out['sum'    ] = sum(operand)
    out['stddev' ] = statistics.pstdev(operand, out['average'])
    lower = [value for value in operand if value < out['median']]
    upper = [value for value in operand if value > out['median']]
    out['q1'] = statistics.median(lower)
    out['q3'] = statistics.median(upper)
    return out

  def handle_sort(self, children):
    operand = self.process_operands(children)[0]
    if isinstance(operand, str):
      out = ''.join(sorted(operand))
    elif isinstance(operand, (int, float)):
      out = operand
    elif isinstance(operand, dict):
      out = sorted(operand.values())
    else:
      out = sorted(operand)
    return out
  
  def handle_shuffle(self, children):
    operand = self.process_operands(children)[0][:]
    if isinstance(operand, str):
      operand = list(operand)
      random.shuffle(operand)
      out = ''.join(operand)
    else:
      random.shuffle(operand)
      out = operand
    return out

  def handle_slices(self, slice_type, children):
    operands = self.process_operands(children)
    v = operands[0]
    args = operands[1:]
    
    if slice_type == 'whole_slice':
      out = v[:]
    elif slice_type == 'start_slice':
      out = v[args[0]:]
    elif slice_type == 'start_step_slice':
      out = v[args[0]::args[1]]
    elif slice_type == 'start_stop_slice':
      out = v[args[0]:args[1]]
    elif slice_type == 'fine_slice':
      out = v[args[0]:args[1]:args[2]]
    elif slice_type == 'stop_slice':
      out = v[:args[0]]
    elif slice_type == 'stop_step_slice':
      out = v[:args[0]:args[1]]
    elif slice_type == 'step_slice':
      out = v[::args[0]]
    elif slice_type == 'not_a_slice':
      if isinstance(args[0], Function):
        e = f'Functions cannot be used as keys or indices. ({args[0]!r})'
        raise TypeError(e)
      out = v[args[0]]
    return out

  def handle_plugin_call(self, children):
    plugin_alias, argument = self.process_operands(children)
    operation = plugins.lookup(plugin_alias)
    return operation(argument)
  
  def handle_dice(self, roll_type, children):
    result_type, _, keep_mode = roll_type.split('_')
    operands = self.process_operands(children[::2])
    dice, sides = operands[:2]
    count = operands[2] if len(operands) > 2 else None
    as_sum = result_type == 'scalar'
    return util.roll(dice, sides, count, mode=keep_mode, return_sum=as_sum)

  def handle_apply(self, children):
    function, iterable = self.process_operands(children)
    out = [ ]
    for item in iterable:
      out.append(function(self.scoping_data, self, item))
    return out

  def handle_function_call(self, children):
    operands = self.process_operands(children)
    function = operands[0]
    arguments = operands[1:]
    return function(self.scoping_data, self, *arguments)

  def handle_getattr(self, children):
    operands = self.process_operands(children)
    obj = operands[0]
    out = obj
    for attr in operands[1:]:
      out = out[attr.name]
    return out

  def handle_search(self, children):
    text, pattern = [self.handle_instruction(c) for c in children[0::2]]
    p = re.compile(pattern)
    match = p.search(text)
    if match is None:
      start = -1
      end   = -1
    else:
      start = match.start()
      end   = match.end()
    return {'start' : start, 'end' : end}
  
  def handle_match(self, children):
    text, pattern = [self.handle_instruction(c) for c in children[0::2]]
    p = re.compile(pattern)
    match = p.match(text)
    return match is not None
  
  def handle_number_literal(self, children):
    child = children[-1]
    try:
      x = int(child.value)
      f = float(child.value)
    except ValueError:
      x = None
      f = float(child.value)
    return x if x == f else f
  
  def handle_boolean_literal(self, children):
    return eval(children[-1].value)

  def handle_string_literal(self, children):
    return eval(children[-1].value)
  
  def handle_list_literal(self, children):
    if children:
      out = self.process_operands(children)
    else:
      out = [ ]
    return out
  
  def handle_list_range_literal(self, children):
    return [x for x in range(*self.process_operands(children))]
  
  def handle_closed_list_literal(self, children):
    operands = self.process_operands(children)
    step = operands[2] if len(operands) == 3 else 1
    start, stop = operands[0], operands[1] + 1
    if start > stop and step == 1:
      step *= -1
    return [x for x in range(start, stop, step)]

  def handle_dict_literal(self, children):
    pairs = { }
    if children:
      for c in children:
        k, v = self.process_operands(c.children)
        pairs[k] = v
    return pairs


  def handle_identifiers(self, identifier_type, children):
    mode, _ = identifier_type.split('_')
    name = children[-1].value
    return Identifier(
      name,
      self.scoping_data,
      mode,
      self.public,
      self.shared,
      self.private,
      self.core)

