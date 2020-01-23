#!/usr/bin/python3

import parser
import dice

class Interpreter(object):
  def __init__(self):
    self.parser = parser.get_parser()
  
  def execute(self, command):
    tree = self.parser.parse(command)
    
    return self.interpret(tree)
    
  def interpret(self, tree):
    return handle_instruction(tree)
      
def handle_instruction(tree):
  if tree.data == 'start':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'expression':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'simple_assignment':
    print(tree.children)
    out = tree.data
  elif tree.data == 'bool_or':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_or':
    print(tree.children)
    out = tree.data
  elif tree.data == 'bool_xor':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_xor':
    print(tree.children)
    out = tree.data
  elif tree.data == 'bool_and':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_and':
    print(tree.children)
    out = tree.data
  elif tree.data == 'bool_not':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'logical_not':
    print(tree.children)
    out = tree.data
  elif tree.data == 'comp':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'greater_than':
    print(tree.children)
    out = tree.data
  elif tree.data == 'greater_equal':
    print(tree.children)
    out = tree.data
  elif tree.data == 'equal':
    print(tree.children)
    out = tree.data
  elif tree.data == 'not_equal':
    print(tree.children)
    out = tree.data
  elif tree.data == 'less_equal':
    print(tree.children)
    out = tree.data
  elif tree.data == 'less_than':
    print(tree.children)
    out = tree.data
  elif tree.data == 'shift':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'left_shift':
    print(tree.children)
    out = tree.data
  elif tree.data == 'right_shift':
    print(tree.children)
    out = tree.data
  elif tree.data == 'arithm':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'addition':
    print(tree.children)
    out = tree.data
  elif tree.data == 'subtraction':
    print(tree.children)
    out = tree.data
  elif tree.data == 'catenation':
    print(tree.children)
    out = tree.data
  elif tree.data == 'term':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'multiplication':
    print(tree.children)
    out = tree.data
  elif tree.data == 'division':
    print(tree.children)
    out = tree.data
  elif tree.data == 'remainder':
    print(tree.children)
    out = tree.data
  elif tree.data == 'floor_division':
    print(tree.children)
    out = tree.data
  elif tree.data == 'factor':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'negation':
    print(tree.children)
    out = tree.data
  elif tree.data == 'idempotence':
    print(tree.children)
    out = tree.data
  elif tree.data == 'power':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'exponent':
    print(tree.children)
    out = tree.data
  elif tree.data == 'logarithm':
    print(tree.children)
    out = tree.data
  elif tree.data == 'die':
    out = handle_instruction(tree.children[0])
  elif tree.data == 'scalar_die':
    left = handle_instruction(tree.children[0])
    right = handle_instruction(tree.children[1])
    out = dice.roll_kernel(left, right)
  elif tree.data == 'vector_die':
    print(tree.children)
    out = tree.data
  elif tree.data == 'atom':
    print(tree.children)
    token = tree.children[0]
    out = handle_atoms(token)
  return out

def handle_atoms(token):
  if token.type == 'NUMBER':
    f = float(token.value)
    x = int(token.value)
    out = x if x == f else f
  return out

if __name__ == '__main__':
  dicelark = Interpreter()
  x = dicelark.execute('1d6')
  print(x)
