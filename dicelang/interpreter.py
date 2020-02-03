#!/usr/bin/env python3
import os
import pytest
from lark import Lark
from dicelang import kernel
from dicelang import grammar
from dicelang import datastore

default_path = 'vars'

class Interpreter(object):
  def __init__(self):
    self.parser = Lark(grammar.raw_text, start='start', parser='earley')
    self.datastore = datastore.Persistence()
  
  def execute(self, command, user, server):
    tree = self.parser.parse(command)
    return self.interpret(tree, user, server)
    
  def interpret(self, tree, user, server):
    return kernel.handle_instruction(tree, user, server, self.datastore)
  

