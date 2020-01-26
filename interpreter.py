#!/usr/bin/python3

import sys
from lark import Lark

import kernel
import datastore

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


def main(*args):
  filename = args[1]
  dicelark = Interpreter('grammar.lark')
  user     = 'Tester'
  server   = 'Test Server'
  with open(filename, 'r') as test_file:
    for line in test_file:
      line = line.strip()
      if line:
        x = dicelark.execute(line, user, server)
        print(line, '->', x)
  datastore.save_all()
  return 0

if __name__ == '__main__':
  exit_code = main(*sys.argv)
  sys.exit(exit_code)


