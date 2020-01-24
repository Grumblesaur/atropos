#!/usr/bin/python3

import sys
from lark import Lark

import kernel

class Interpreter(object):
  def __init__(self, grammar_file_name, debug=False):
    with open(grammar_file_name, 'r') as grammar_file:
      grammar = grammar_file.read()
    if not grammar:
      raise ValueError('grammar file renamed or missing!')
    self.parser = Lark(grammar)
    self.debug  = debug
  
  def execute(self, command):
    tree = self.parser.parse(command)
    if self.debug:
      print(tree, '\n')
    return self.interpret(tree)
    
  def interpret(self, tree):
    return kernel.handle_instruction(tree)


def main(*args):
  filename = args[1]
  dicelark = Interpreter('grammar.lark')
  with open(filename, 'r') as test_file:
    for line in test_file:
      line = line.strip()
      if line:
        x = dicelark.execute(line)
        print(line, '->', x)
  return 0

if __name__ == '__main__':
  exit_code = main(*sys.argv)
  sys.exit(exit_code)


