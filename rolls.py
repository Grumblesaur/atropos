import random
import enum

def kernel(dice, sides, count=0, mode='all', return_sum=True):
  results = [random.randint(1, sides) for die in range(dice)]
  if mode == 'lowest':
    out = sorted(results)[:count]
  elif mode == 'highest':
    out = sorted(results, reverse=True)[:count]
  else:
    out = results
  return sum(out) if return_sum else out


