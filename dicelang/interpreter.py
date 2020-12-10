#!/usr/bin/env python3
import os
from lark import Lark
from dicelang import visitor
from dicelang import grammar
from dicelang import datastore
from dicelang import ownership

class Interpreter(object):
  GLOBAL_ID = -1
  def __init__(self):
    self.parser = Lark(grammar.raw_text, start='start', parser='earley')
    self.vars_directory = os.environ.get('DICELANG_DATASTORE', 'vars')

    if not os.path.isdir(self.vars_directory):
      os.mkdir(self.vars_directory)
    
    self.datastore = datastore.DataStore()
    self.visitor = visitor.Visitor(self.datastore)
  
  def keys(self, mode, owner_id=GLOBAL_ID):
    return self.datastore.view(mode, owner_id)
  
  def execute(self, command, user, server):
    '''Passes the abstract syntax tree generated by the parser to the
    interpreter kernel with the user's name and the server's name for
    variable retrieval and emplacement. The result is stored in the
    variable known as `_`. The private `_` is intended to be the last
    result by that user, the server `_` is intended to be the last result
    on that server, and the public `_` is intended to be the last result
    by any command passed to the interpreter.'''
    tree = self.parser.parse(command)
    scoping_data = ownership.ScopingData(user, server) 
    value, printout = self.visitor.walk(tree, scoping_data, True)
    self.datastore.put(user, '_', value, 'private')
    self.datastore.put(server, '_', value, 'server')
    self.datastore.put(Interpreter.GLOBAL_ID, '_', value, 'global')
    return (value, printout)
  
  def get_print_queue_on_error(self, user):
    return self.visitor.get_print_queue_on_error(user)

