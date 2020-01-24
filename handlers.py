import math
import rolls
import kernel

def handle_power(children):
  mantissa = kernel.handle_instruction(children[0])
  exponent = kernel.handle_instruction(children[1])
  return mantissa ** exponent

def handle_logarithm(children):
  base = kernel.handle_instruction(children[0])
  anti = kernel.handle_instruction(children[1])
  return math.log(anti, base)

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

def handle_atom(token):
  if token.type == 'NUMBER':
    try:
      x = int(token.value)
      f = float(token.value)
    except ValueError:
      x = None
      f = float(token.value)
    out = x if x == f else f
  return out


