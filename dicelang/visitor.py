import copy
import math
import random
import re
import statistics
import time

from collections.abc import Iterable
from dicelang import plugins
from dicelang import util

from dicelang.float_special import inf
from dicelang.float_special import nan
from dicelang.float_special import numeric_types

from dicelang.exceptions import BreakSignal
from dicelang.exceptions import SkipSignal
from dicelang.exceptions import ReturnSignal

from dicelang.exceptions import AliasError
from dicelang.exceptions import BreakError
from dicelang.exceptions import DiceRollTimeout
from dicelang.exceptions import DoWhileLoopTimeout
from dicelang.exceptions import ExecutionTimeout
from dicelang.exceptions import ExponentiationTimeout
from dicelang.exceptions import OperationError
from dicelang.exceptions import ReturnError
from dicelang.exceptions import SkipError
from dicelang.exceptions import WhileLoopTimeout

from dicelang.function import Function
from dicelang.alias import Alias
from dicelang.undefined import Undefined

from dicelang.identifier import Identifier
from dicelang.ownership import ScopingData
from dicelang.print_queue import PrintQueue

from dicelang.validator import IntegerValidator

class Visitor(object):
  def __init__(self, data, timeout=12):
    self.variable_data = data
    self.scoping_data = None
    
    # Timeout is parameterized as its value may vary due to load in later
    # versions of Atropos.
    self.loop_timeout = timeout
    self.execution_timeout = timeout * 3
    self.depth = 0
    self.must_finish_by = None
    self.print_queue = PrintQueue()
  
  def get_print_queue_on_error(self, user):
    '''Reset the interpreter for the next command and release all
    debug output to the user.'''
    self.depth = 0
    return self.print_queue.flush(user)
    
  def walk(self, parse_tree, scoping_data, from_interpreter=False):
    '''Start execution of a syntax tree.'''
    if from_interpreter:
      self.must_finish_by = self.execution_timeout + time.time()
    self.scoping_data = scoping_data
    
    self.depth += 1
    try:
      result = self.handle_instruction(parse_tree)
    except BreakSignal:
      raise BreakError()
    except SkipSignal:
      raise SkipError()
    except ReturnSignal as rs:
      if self.depth == 1:
        raise ReturnError()
      result = rs.data
    self.depth -= 1
    
    # Reentrancy case -- when a dicelang Function is executed,
    # we don't want to erase our scoping data since we're still
    # pushing and popping stack frames. When depth is zero, we
    # are finished executing. Furthermore, we only want to return
    # the current working value to the previous depth level; print
    # queue output doesn't come until we bottom out at depth=0.
    tmp_user = self.scoping_data.user
    if not self.depth:
      out = (result, self.print_queue.flush(self.scoping_data.user))
      self.scoping_data = None
    else:
      out = result
    return out
  
  def process_operands(self, children):
    '''Avoid typing the following list comprehension in a majority
    of handlers.'''
    return [self.handle_instruction(c) for c in children]
  
  def handle_instruction(self, tree):
    '''Dispatch execution recursively through the syntax tree.'''
    
    # Each time we address a new instruction, we check to see if we've
    # taken longer than we promised to at the start of the interpreter call.
    # If we have, then we must bail out and report failure to the user.
    now = time.time()
    if now > self.must_finish_by:
      e = ' '.join([
        'Dicelang command took too long! You may have chained',
        'too many dice together, constructed an extremely large number,',
        'or just used a lot of different operations.'
      ])
      raise ExecutionTimeout(e)
    
    if tree.data == 'start':
      out = [self.handle_instruction(c) for c in tree.children][-1]
    elif tree.data == 'block' or tree.data == 'short_body':
      out = self.handle_block(tree.children)
    elif tree.data == 'function':
      out = self.handle_function(tree.children)
    elif tree.data == 'alias':
      out = self.handle_alias(tree.children)
    elif tree.data == 'inspection':
      out = self.handle_inspection(tree.children)
    
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
    elif tree.data == 'standard_getattr_import':
      out = self.handle_standard_getattr_import(tree.children)
    elif tree.data == 'as_import':
      out = self.handle_as_import(tree.children)
    elif tree.data == 'as_getattr_import':
      out = self.handle_as_getattr_import(tree.children)
    
    elif tree.data == 'deletion':
      out = self.handle_deletion(tree.children)
    elif tree.data == 'deletable':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'deletable_variable':
      out = self.handle_deletable_variable(tree.children)
    elif tree.data == 'deletable_element':
      out = self.handle_deletable_element(tree.children)
    elif tree.data == 'deletable_attribute':
      out = self.handle_deletable_attribute(tree.children)
    
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
    
    elif tree.data == 'reflection':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'typeof':
      out = self.handle_typeof(tree.children)
    
    elif tree.data == 'print':
      out = self.handle_instruction(tree.children[0])
    elif tree.data == 'printline':
      out = self.handle_print(tree.children, '\n')
    elif tree.data == 'printword':
      out = self.handle_print(tree.children, ' ')
    
    elif tree.data in ('break', 'skip', 'return'):
      out = self.handle_instruction(tree.children[0])
    elif tree.data in ('break_expr', 'skip_expr', 'return_expr'):
      out = self.handle_signal(tree.children, bare=False)
    elif tree.data in ('break_bare', 'skip_bare', 'return_bare'):
      out = self.handle_signal(tree.children, bare=True)
    
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
    elif tree.data == 'tuple_literal':
      out = self.handle_instruction(tree.children[0])
    elif tree.data in ('mono_tuple', 'multi_tuple', 'empty_tuple'):
      out = self.handle_tuple(tree.children)
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
    
    if isinstance(out, Alias):
      out = out(self)
      
    return out 
    
    
  def handle_block(self, children):
    '''Compound expression consisting of `;`-separated expressions and
    evaluating to the last expression in the sequence.'''
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
    closed = self.scoping_data.calling_environment()
    out = Function(code, param_names=params, closed_vars=closed)
    out.visitor = self
    return out
  
  def handle_alias(self, children):
    '''Builds a custom alias object.'''
    identifier = self.handle_instruction(children[0])
    aliased = self.handle_instruction(children[1])
    
    if not isinstance(aliased, Function):
      e = f'Value of type {aliased.__class__.__name__} cannot be aliased.'
      e += ' Only a Function can be aliased.'
      raise AliasError(e)
    
    out = Alias(aliased)
    identifier.put(out)
    return out.aliased
  
  def handle_inspection(self, children):
    identifier = self.handle_instruction(children[1])
    obj = identifier.get()
    if isinstance(obj, Alias):
      out = obj.aliased
    else:
      out = obj
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
        try:
          self.scoping_data.get_scope()[name] = element
          results.append(self.handle_instruction(children[2]))
        except BreakSignal as bs:
          if bs.is_set:
            results.append(bs.data)
          break
        except SkipSignal as ss:
          if ss.is_set:
            results.append(ss.data)
          continue
      
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
      if time.time() > timeout:
        times = len(results)
        raise WhileLoopTimeout(times)
      try:
        results.append(self.handle_instruction(children[1]))
      except BreakSignal as bs:
        if bs.is_set:
          results.append(bs.data)
        break
      except SkipSignal as ss:
        if ss.is_set:
          results.append(ss.data)
        continue
    self.scoping_data.pop_scope()
    return results
 
  def handle_do_while_loop(self, children):
    '''Same as a while loop, but is guaranteed to execute at least once.'''
    self.scoping_data.push_scope()
    results = [self.handle_instruction(children[0])]
    timeout = time.time() + self.loop_timeout
    while self.handle_instruction(children[1]):
      if time.time() > timeout:
        times = len(results)
        raise DoWhileLoopTimeout(times)
      try:
        results.append(self.handle_instruction(children[0]))
      except BreakSignal as bs:
        if bs.is_set:
          results.append(bs.data)
        break
      except SkipSignal as ss:
        if ss.is_set:
          results.append(ss.data)
        continue 
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
    '''Copies a variable by value to a new variable with the same name in the
    server-level namespace.'''
    ident = self.handle_instruction(children[1])
    value = copy.deepcopy(ident.get())
    new_name = ident.name
    mode = 'server'
    if value is not Undefined:
      imported = Identifier(new_name, self.scoping_data, mode, self.variable_data)
      imported.put(value)
      out = True
    else:
      out = False
    return out
      
  def handle_standard_getattr_import(self, children):
    operands = self.process_operands(children[1:])
    ident = operands[0]
    try:
      name = ident.name
      val = ident.get()
      for attr in operands[1:]:
        name = attr.name
        val = val[name]
      imported = Identifier(name, self.scoping_data, 'server', self.variable_data)
      print(val)
      imported.put(copy.deepcopy(val))
      out = True
    except (KeyError, AttributeError) as e:
      print(e)
      out = False
    return out
      
  def handle_as_import(self, children):
    '''Copies a variable by value to a new variable with a different name.'''
    importable, alias = [self.handle_instruction(c) for c in children[1:]]
    value = importable.get()
    new_name = alias.name
    if value is not Undefined:
      imported = Identifier(
        new_name,
        self.scoping_data,
        alias.mode,
        self.variable_data)
      imported.put(copy.deepcopy(value))
      out = True
    else:
      out = False
    return out
  
  def handle_as_getattr_import(self, children):
    try:
      operands = self.process_operands(children[1:])
      idents = operands[:-1]
      new_name = operands[-1].name
      mode = operands[-1].mode
      value = idents[0].get()
      for attr in idents[1:]:
        value = value[attr.name]
      imported = Identifier(
        new_name,
        self.scoping_data,
        mode,
        self.variable_data)
      imported.put(copy.deepcopy(value))
      out = True
    except (KeyError, AttributeError):
      out = False
    return out
  
  def handle_deletion(self, children):
    out = tuple(self.process_operands(children))
    if len(out) == 1:
      out = out[0]
    return out
  
  def handle_deletable_variable(self, children):
    ident = self.handle_instruction(children[0])
    out = ident.drop()
    print(out)
    return out

  def handle_deletable_element(self, children):
    '''Construct a Python code string that will delete from the possibly-
    nested dict object, and exec it to remove the key-value pair from the
    dict. The value is returned.'''
    ident = self.handle_instruction(children[0])
    subscripts = [self.handle_instruction(c) for c in children[1:]]
    subscripts = ''.join([f'[{s!r}]' for s in subscripts])
    target = ident.get()
    val_repr = f'target{subscripts}'
    
    with Function.SerializableRepr() as _:
      out = eval(val_repr)
      exec(f'del {val_repr}')
    
    ident.put(target)
    return out

  def handle_deletable_attribute(self, children):
    '''Similar to delete element, but this results from a chain of `.`
    accesses, and not `[x]` indexes.'''
    ident = self.handle_instruction(children[0])
    subscripts = [self.handle_instruction(c) for c in children[1:]]
    subscripts = ''.join([f'[{id_.name!r}]' for id_ in subscripts])
    target = ident.get()
    val_repr = f'target{subscripts}'
    with Function.SerializableRepr():
      out = eval(val_repr)
      exec(f'del {val_repr}')
    ident.put(target)
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
        raise OperationError(error)
    subscripts = ''.join([f'[{s!r}]' for s in subscripts])
    target = ident.get()
    
    with Function.SerializableRepr() as _:
      stmt = f'target{subscripts} = {value!r}'
      exec(stmt)
    ident.put(target) # update the database and not just the cache
    return value
  
  def handle_setattr(self, children):
    '''Handle the assignment of a value to an arbitrarily-chained attribute
    of a variable.'''
    value = self.handle_instruction(children[-1])
    ident = self.handle_instruction(children[0])
    attr_chain = [self.handle_instruction(c) for c in children[1:-1]]
    subscripts = ''.join([f'[{attr.name!r}]' for attr in attr_chain])
    target = ident.get()
    
    with Function.SerializableRepr() as _:
      stmt = f'target{subscripts} = {value!r}'
      exec(stmt)
    ident.put(target)
    return value

  def handle_inline_if(self, children):
    '''Shorthand Python-like inline if-else expression.'''
    condition = self.handle_instruction(children[1])
    i = 0 if condition else 2
    return self.handle_instruction(children[i])
  
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
    '''Boolean disjunction of two objects, with short circuit behavior.'''
    left = self.handle_instruction(children[0])
    if left:
      out = left
    else:
      out = self.handle_instruction(children[1])
    return out
  
  def handle_logical_xor(self, children):
    '''Boolean exclusive disjunction of two objects.'''
    left, right = self.process_operands(children)
    return (left or right) and not (left and right)
  
  def handle_logical_and(self, children):
    '''Boolean conjunction of two objects, with short circuit behavior.'''
    left = self.handle_instruction(children[0])
    if left:
      out = self.handle_instruction(children[1])
    else:
      out = left
    return out

  def handle_logical_not(self, children):
    '''Boolean negation of an object.'''
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
    '''Integer leftward bit shift. "Rotates" iterables.'''
    return util.shift(*self.process_operands(children))
  
  def handle_right_shift(self, children):
    '''Integer rightward bit shift. "Rotates" iterables.'''
    return util.shift(*self.process_operands(children), left_shift=False)
  
  def handle_addition(self, children):
    '''Numeric addition or concatenation of ordered iterables.'''
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
        raise OperationError(str(e))
    return result

  def handle_catenation(self, children):  
    '''Joins two numbers via their representation of digit strings.'''
    numbers = self.process_operands(children)
    intstrings = map(lambda x: str(int(x)), numbers)
    return int(''.join(intstrings))

  def handle_multiplication(self, children):
    '''Handles multiplication of numerics and the repetition of ordered
    iterables.'''
    factor1, factor2 = self.process_operands(children)
    array = (list, str)
    if isinstance(factor1, array) and isinstance(factor2, numeric_types):
      out = util.iterable_repetition(factor1, factor2)
    elif isinstance(factor1, numeric_types) and isinstance(factor2, array):
      out = util.iterable_repetition(factor2, factor1)
    else:
      out = factor1 * factor2
    return out

  def handle_division(self, children):
    '''Ordinary floating point division.'''
    dividend, divisor = self.process_operands(children)
    if divisor == 0:
      sign = 1 if dividend >= 0 else -1
      sign *= 1 if divisor >= 0 else -1
      out = sign * inf
    else:
      out = dividend / divisor
    return out
  
  def handle_remainder(self, children):
    '''Remainder for float or int.'''
    dividend, divisor = self.process_operands(children)
    if divisor == 0 and isinstance(dividend, numeric_types):
      out = nan
    else:
      out = dividend % divisor
    return out
  
  def handle_floor_division(self, children):
    '''Divide and always round down, returning integer.'''
    dividend, divisor = self.process_operands(children)
    if divisor == 0:
      sign = 1 if dividend >= 0 else -1
      sign *= 1 if divisor >= 0 else -1
      out = sign * inf
    else:
      out = dividend // divisor
    return out
  
  def handle_negation(self, children):
    '''Get the arithmetic inverse of a numeric value, or the reverse of
    some ordered iterable.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, (list, str, tuple)):
      out = operand[::-1]
    else:
      out = -operand
    return out
  
  def handle_absolute_value(self, children):
    '''Get the absolute value of a numeric while keeping the same type;
    no-op on non-numerics.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, (float, int)):
      out = operand if operand >= 0 else -operand
    elif isinstance(operand, complex):
      out = operand.conjugate()
    else:
      out = operand
    return out
    
  def handle_exponent(self, children):
    '''Handle exponents, which are strictly numeric (for now). Use inelegant
    iterated multiplication for integer powers in order to allow for timeout
    checks for when an extremely large number is being constructed.'''
    mantissa, exponent = self.process_operands(children)
    non_ints = (float, complex)
    if isinstance(exponent, non_ints) and isinstance(mantissa, numeric_types):
      out = mantissa ** exponent
    elif isinstance(exponent, int) and isinstance(mantissa, numeric_types):
      e = ExponentiationTimeout('Base or exponent too large in magnitude!')
      out = 1
      if exponent != 0:
        for x in range(abs(exponent)):
          if time.time() > self.must_finish_by:
            raise e
          out = out * mantissa
        if exponent < 0:
          out = 1 / out
      else:
        if mantissa == 0:
          out = nan
        else:
          out = 1 # nonzero to the power zero is always 1
    else:
      raise OperationError('Operands to exponentiation (**) must be numeric!')
    return out
  
  def handle_logarithm(self, children):
    '''Logarithm is overloaded with a format syntax in analogy with `%` being
    overloaded with an interpolation syntax.'''
    base, exponent = self.process_operands(children)
    if isinstance(base, str):
      out = util.string_format(base, exponent)
    else:
      out = math.log(exponent, base)
    return out

  def handle_sum_or_join(self, children):
    '''Sum a list of numbers or concatenate a |list of strings|, or
    |list of lists/tuples|, or |list of dicts|. For a complex number,
    this will give the imaginary part.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, Iterable) and operand:
      out = operand[0]
      for element in operand[1:]:
        out += element
    elif isinstance(operand, Iterable) and not operand:
      out = 0
    elif isinstance(operand, complex):
      out = operand.imag
    else:
      out = operand
    return out

  def handle_length(self, children):
    '''Obtain the length of an iterable. For a complex number,
    this will give the real part.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, Iterable):
      out = len(operand)
    elif isinstance(operand, Function):
      out = len(operand.params)
    elif isinstance(operand, complex):
      out = operand.real
    else:
      out = 0
    return out
  
  def handle_selection(self, children):
    '''Select a random element from an iterable.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, numeric_types):
      operand = [operand]
    elif isinstance(operand, dict):
      operand = [[key, value] for key, value in operand.items()]
    return random.choice(operand)

  def handle_extrema(self, children, extremum_type):
    '''Find max or min, depending on the speciifcs of the parse tree.'''
    operand = self.process_operands(children)[0]
    if not isinstance(operand, Iterable):
      operand = [operand]
    return min(operand) if extremum_type == 'minimum' else max(operand)
  
  def handle_flatten(self, children):
    '''Iterates through an arbitrarily-nested iterable and feeds all the scalar
    values into a new list, which is returned.'''
    return util.flatten(self.process_operands(children)[0])
  
  def handle_stats(self, children):
    '''Generate a number summary from some iterable.'''
    operand = self.process_operands(children)[0]
    out = { }
    if isinstance(operand, numeric_types):
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
    '''Return a sorted copy of an iterable.'''
    operand = self.process_operands(children)[0]
    if isinstance(operand, str):
      out = ''.join(sorted(operand))
    elif isinstance(operand, numeric_types):
      out = operand
    elif isinstance(operand, dict):
      out = sorted(operand.values())
    else:
      out = sorted(operand)
    return out
  
  def handle_shuffle(self, children):
    '''Return a shuffled copy of an iterable.'''
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
    '''Handle slicing, indexing, and dict value retrieval.'''
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
        raise OperationError(e)
      out = v[args[0]]
    return out

  def handle_plugin_call(self, children):
    '''Find a plugin by the alias provided as the left operand and execute it
    with the right operand as an argument.'''
    plugin_alias, argument = self.process_operands(children)
    operation = plugins.lookup(plugin_alias)
    return operation(argument)
  
  def handle_dice(self, roll_type, children):
    '''Scan the dice subtree for specifics and then call the utility function
    to do the actual random generation.'''
    result_type, _, keep_mode = roll_type.split('_')
    operands = self.process_operands(children[::2])
    dice, sides = operands[:2]
    count = operands[2] if len(operands) > 2 else None
    as_sum = result_type == 'scalar'
    
    # Extremely large rolls (a number of dice with 10+ digits; 10+ digit sides
    # is fine) will cause the validator to raise an exception, which is written
    # here, and which will be visible to the user if this occurs.
    e = ' '.join([
      f'{dice} is too many dice! This operation may take too long,'
      'potentially preventing other users from being able to roll dice too.'])
    IntegerValidator(10, DiceRollTimeout).validate(dice, e)
    
    return util.roll(dice, sides, count, keep_mode, as_sum)
  
  def handle_apply(self, children):
    '''Accepts a function as the left operand, and some iterable (usually a
    list) as the right operand. The function is executed on each element of the
    iterable, and the results are returned in a list in the order they were
    processed.'''
    function, iterable = self.process_operands(children)
    return [function(self, x) for x in iterable]
  
  def handle_function_call(self, children):
    '''Evaluate the arguments and call the function with them. If the called
    object is not a function, try to treat the operation as multiplication.
    e.g. a(x, y) -> (a*x, a*y)'''
    operands = self.process_operands(children)
    function_or_other = operands[0]
    arguments = operands[1:]
    
    if isinstance(function_or_other, Function):
      try:
        out = function_or_other(self, *arguments)
      except ReturnSignal as rs:
        out = rs.data
      except BreakSignal as bs:
        raise BreakError()
      except SkipSignal as ss:
        raise SkipError(ss.msg)
    elif isinstance(function_or_other, numeric_types):
      out = tuple([function_or_other * x for x in arguments])
      out = out[0] if len(out) == 1 else out
    else:
      cls_name = function_or_other.__class__.__name__
      e = f'Cannot call object of type {cls_name} as '
      e += 'function nor multiply it as a coefficient.'
      raise OperationError(e)
    return out

  def handle_getattr(self, children):
    '''Handle field lookup by `.` operator.'''
    operands = self.process_operands(children)
    obj = operands[0]
    out = obj
    for attr in operands[1:]:
      out = out[attr.name]
    return out

  def handle_search(self, children):
    '''Handle the `seek` regular expression operator.'''
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
    '''Handle the `like` regular expression operator.'''
    text, pattern = [self.handle_instruction(c) for c in children[0::2]]
    p = re.compile(pattern)
    match = p.match(text)
    return match is not None
  
  def handle_typeof(self, children):
    '''Generates a string describing the type of an object.'''
    obj = self.handle_instruction(children[1])
    if isinstance(obj, Function):
      out = 'func'
    else:
      out = type(obj).__name__
    return out
  
  def handle_print(self, children, trailer):
    '''Adds the value of an expression to the print queue
    and returns the value of the expression.'''
    value = self.process_operands(children[1:])[0]
    msg = str(value) + trailer
    self.print_queue.append(self.scoping_data.user, msg)
    return value
  
  def handle_signal(self, children, bare):
    data = None if bare else self.process_operands(children[1:])[0]
    sig_type = children[0].value
    raise {
      'break'  : BreakSignal,
      'skip'   : SkipSignal,
      'return' : ReturnSignal
    }[sig_type](data)
  
  def handle_number_literal(self, children):
    '''Constructs an int or float from a numeric literal.'''
    child = children[-1]
    
    def try_parse_as(num_type, value):
      try:
        out = num_type(value)
      except (ValueError, TypeError):
        out = None
      return out
    
    x = try_parse_as(int, child.value)
    f = try_parse_as(float, child.value)
    c = try_parse_as(complex, child.value)
    
    if x is not None:
      return x
    if f is not None:
      return f
    
    if c is not None:
      out = c
    else:
      raise ValueError(f'{child.value!r} could not be parsed as a numeric!')
    return out
  
  def handle_boolean_literal(self, children):
    '''Constructs a bool from the literal syntax.'''
    return eval(children[-1].value)

  def handle_string_literal(self, children):
    '''Constructs a string from the literal syntax.'''
    return eval(children[-1].value)
  
  def handle_list_literal(self, children):
    '''Constructs a list literal from the literal syntax.'''
    if children:
      out = self.process_operands(children)
    else:
      out = [ ]
    return out
  
  def handle_list_range_literal(self, children):
    '''Constructs a list literal on the interval [1, n).'''
    return util.range_list(False, *self.process_operands(children))
  
  def handle_closed_list_literal(self, children):
    '''Constructs a list on the interval [1, n].'''
    return util.range_list(True, *self.process_operands(children))
  
  def handle_tuple(self, children):
    '''Constructs a tuple from the literal syntax.'''
    if children:
      out = tuple(self.process_operands(children))
    else:
      out = ()
    return out
  
  def handle_dict_literal(self, children):
    '''Constructs a dict from the literal syntax.'''
    pairs = { }
    if children:
      for c in children:
        k, v = self.process_operands(c.children)
        pairs[k] = v
    return pairs


  def handle_identifiers(self, identifier_type, children):
    '''Creates an identifier appropriate for the appropriate access
    type and current scope.'''
    mode, _ = identifier_type.split('_')
    name = children[-1].value
    return Identifier(
      name,
      self.scoping_data,
      mode,
      self.variable_data)

