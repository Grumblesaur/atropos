import time
import random
import numbers

from dicelang.function import Function
from dicelang.exceptions import DiceRollTimeout

def is_noninteger(x):
  '''Used to detect float and complex numbers as numbers.Real will also
  include integers.'''
  p = isinstance(x, numbers.Number)
  q = isinstance(x, numbers.Integral)
  return p and not q

def is_nonkey(x):
  '''We don't allow dicts to be keyed by these non-hashable objects.
  This function is used instead to allow the Visitor to raise a more
  useful error for users than Python would raise itself.'''
  return isinstance(x, (dict, list, Function))

def addition(left, right):
  '''Adds special rules to auto-box scalar items when they are added to
  a list, as well as for merging two dicts via '+'. Otherwise, behaves as
  you would expect from python.'''
  if isinstance(left, list) and not isinstance(right, list):
    out = left + [right]
  elif isinstance(right, list) and not isinstance(left, list):
    out = [left] + right
  elif isinstance(left, dict) and isinstance(right, dict):
    out = {**left, **right}
  else:
    out = left + right
  return out

def shift(left, right, left_shift=True):
  '''Adds special rules for 'bitwise shift' operators. When the left operand is
  a list and the right is an int, this "rotates" the list. Left shifts pop from
  back and push to the front of the list, while right shifts pop from the front
  of the list and push to the back.
  
  When the left operand is a floating point number and the right is an int, the
  outcome is the value of `left` rounded to `right` decimal places. The
  direction of the shift does not matter for this case.
  
  Otherwise, shift normally, possibly raising an exception.'''
  out = None
  if isinstance(left, list) and isinstance(right, int):
    copy = left[:]
    if left_shift:
      for i in range(right):
        p = copy.pop()
        copy.insert(0, p)
    else:
      for i in range(right):
        p = copy.pop(0)
        copy.append(p)
    out = copy
  elif isinstance(left, float) and isinstance(right, int):
    out = round(left, right)
  else:
    out = left << right if left_shift else left >> right
  return out

def iterable_repetition(iterable, repetitions):
  '''Defines the case for when an iterable is multiplied by a number.
  The normal python repetition rules apply for positive numbers, and
  for negatives, the iterable is reversed first.'''
  times = abs(repetitions)
  sign  = repetitions / times if times else 1
  if sign == 1:
    out = iterable * times
  else:
    out = (iterable[::-1]) * times
  return out

def roll(dice, sides, count, mode, return_sum, must_finish_by):
  '''Rolls `dice` dice each with `sides` sides numbered `1` through `sides`.
  When `mode` is "highest", the highest `count` dice are kept; when `mode`
  is "lowest", the lowest `count` dice are kept; oetherwise, all dice are
  kept. `return_sum` is a boolean which causes the dice to be summed if True
  and returned as a list of individual rolls otherwise. `must_finish_by` is
  a time in seconds since the epoch by which the die rolling loop must finish
  executing or else time out.'''
  results = []
  for die in range(dice):
    if time.time() > must_finish_by:
      raise DiceRollTimeout('Took too long rolling dice!')
    results.append(random.randint(1, sides))
  
  if mode == 'lowest':
    out = sorted(results)[:count]
  elif mode == 'highest':
    out = sorted(results, reverse=True)[:count]
  else:
    out = results
  return sum(out) if return_sum else out

def flatten(items, seqtypes=(list, tuple)):
  '''Flattens an arbitrarily nested list or tuple down into a single-depth
  vector (tuple or list, depending on input).'''
  if isinstance(items, tuple):
    revert_to_tuple = True
    items = list(items)
  else:
    revert_to_tuple = False
  
  for i, x in enumerate(items):
    while i < len(items) and isinstance(items[i], seqtypes):
      items[i:i+1] = items[i]
  return tuple(items) if revert_to_tuple else items

def log(msg):
  with open('out.txt', 'a') as f:
    f.write(f'{msg}\n')


def string_format(format_string, fields):
  '''Handles string formatting for %% operator.'''
  if isinstance(fields, dict):
    out = format_string.format(**fields)
  elif isinstance(fields, (list, tuple)):
    out = format_string.format(*fields)
  else:
    out = format_string.format(fields)
  return out

def range_list(closed, start, stop, step=1):
  '''Generates a list of integers from start to stop by step. Step is always
  corrected to the correct sign depending on whether start>stop or not. As
  such, the sign of step does not matter. Closed is a boolean variable that
  determines whether stop should be included in the list.'''
  if start > stop:
    upward = False
    step = -abs(step)
  elif start < stop:
    upward = True
    step = abs(step)
  else:
    return [start] if closed else []
  
  if closed:
    stop += step
  
  out = []
  i = start
  while (upward and i < stop) or (not upward and i > stop):
    out.append(i)
    i += step
   
  return out


