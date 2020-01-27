#!/usr/bin/env python3
import sys
from lark import Lark

import kernel
import datastore
from undefined import Undefined

class Interpreter(object):
  def __init__(self, grammar_file_name, debug=False):
    with open(grammar_file_name, 'r') as grammar_file:
      grammar = grammar_file.read()
    if not grammar:
      raise ValueError('grammar file renamed or missing!')
    self.parser = Lark(grammar, start='start', parser='earley')
    self.debug  = debug
  
  def execute(self, command, user, server):
    tree = self.parser.parse(command)
    if self.debug:
      print(tree, '\n')
    return self.interpret(tree, user, server)
    
  def interpret(self, tree, user, server):
    return kernel.handle_instruction(tree, user, server)


def get_test_cases(filename):
  '''test cases file pointed to by filename must have the following properties:
    * lines are either blank or contain a test case
    * test cases consist of three things in the following order:
      * the command to be executed by the dicelang interpreter
      * the exact sequence of characters '===>' without quotes
      * the value in Python to which the command should resolve'''
  test_cases = [ ]
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if line:
        command, expected = map(lambda s: s.strip(), line.split('===>'))
        test_cases.append((command, eval(expected)))
  return test_cases 

def main(*args):
  try:
    filename = args[1]
  except IndexError:
    print('No filename provided!')
    return 1
  test_cases = get_test_cases(filename)
  interpreter = Interpreter('grammar.lark')
  for command, expected in test_cases:
    print(command)
    actual = interpreter.execute(command, 'Tester', 'Test Server')
    if actual != expected:
      print('actual = {}, expected = {}'.format(actual, expected))
    assert actual == expected
  return 0

if __name__ == '__main__':
  exit_code = main(*sys.argv)
  sys.exit(exit_code)
  
