#!/usr/bin/python3

import sys
import command_parser
import kernel

class Interpreter(object):
  def __init__(self):
    self.parser = command_parser.get_parser()
  
  def execute(self, command):
    tree = self.parser.parse(command)
    return self.interpret(tree)
    
  def interpret(self, tree):
    return kernel.handle_instruction(tree)


def main(*args):
  filename = args[1]
  dicelark = Interpreter()
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


