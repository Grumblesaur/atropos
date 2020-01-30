import random

def iterable_repetition(iterable, repetitions):
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


