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
    '''Passes the abstract syntax tree generated by the parser to the
    interpreter kernel with the user's name and the server's name for
    variable retrieval and emplacement. The result is stored in the
    variable known as `_`. The private `_` is intended to be the last
    result by that user, the server `_` is intended to be the last result
    on that server, and the public `_` is intended to be the last result
    by any command passed to the interpreter.'''
    out = kernel.handle_instruction(tree, user, server, self.datastore)
    self.datastore.private.put(user, '_', out)
    self.datastore.server.put(server, '_', out)
    self.datastore.public.put('_', out)
    return out

