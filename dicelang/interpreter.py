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
    try:
      vars_directory = os.environ['DICELANG_DATASTORE']
      paths = ['{}/{}'.format(vars_directory, name) for name in datastore.names]
    except KeyError:
      if not os.path.isdir(default_path):
        os.mkdir(default_path)
      else:
        for filename in datastore.names:
          path = '{}/{}'.format(default_path, filename)
          if not os.path.isfile(path):
            os.mknod(path)
      paths = ()
    datastore.configure(*paths)
    
  def execute(self, command, user, server):
    tree = self.parser.parse(command)
    return self.interpret(tree, user, server)
    
  @staticmethod
  def interpret(tree, user, server):
    return kernel.handle_instruction(tree, user, server)


