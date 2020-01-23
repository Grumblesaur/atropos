#!/usr/bin/python3

import parser
import dice
import handlers

class Interpreter(object):
  def __init__(self):
    self.parser = parser.get_parser()
  
  def execute(self, command):
    tree = self.parser.parse(command)
    return self.interpret(tree)
    
  def interpret(self, tree):
    return handlers.handle_instruction(tree)

      
if __name__ == '__main__':
  dicelark = Interpreter()
  #x = dicelark.execute('1d6')
  x = dicelark.execute('[]')
  print(x)
