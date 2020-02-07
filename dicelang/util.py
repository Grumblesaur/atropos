import random

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
  sign  = repetitions / times
  if sign == 1:
    out = iterable * times
  else:
    out = (iterable[::-1]) * times
  return out

def roll(dice, sides, count=0, mode='all', return_sum=True):
  results = [random.randint(1, sides) for die in range(dice)]
  if mode == 'lowest':
    out = sorted(results)[:count]
  elif mode == 'highest':
    out = sorted(results, reverse=True)[:count]
  else:
    out = results
  return sum(out) if return_sum else out

def flatten(items, seqtypes=(list, tuple)):
  for i, x in enumerate(items):
    while i < len(items) and isinstance(items[i], seqtypes):
      items[i:i+1] = items[i]
  return items


