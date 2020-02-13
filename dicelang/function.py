import lark
import grammar
from dicelang.bridge import get_function_call_handler
from dicelang.bridge import get_decompiler

class FunctionCallException(Exception):
  pass

length_error = FunctionCallException(
  'Function formal parameters mismatch arguments in length.')
 
class Function(object):
  parser = lark.Lark(grammar.raw_text, start='function', parser='earley')
  
  def __init__(self, tree_or_source, param_names=None):
    self.call_handler = get_function_call_handler()
    decompile = get_decompiler()
    if param_names is None:
      self.source = tree_or_source
      tree = Function.parser.parse(tree_or_source)
      self.code = tree.children[-1]
      self.params = tree.children[0:-1]
    else:
      self.code = tree_or_source
      self.params = param_names
      self.source = '({}) -> {}'.format(
        ', '.join(param_names),
        decompile(tree_or_source))
  
  def __repr__(self):
    return '{}'.format(self.source)
  
  def file_repr(self):
    return 'Function({})'.format(repr(self.source))

  def __call__(self, scoping_data, *args):
    if len(self.params) != len(args):
      raise length_error
    arguments_scope = dict(zip(self.params, args))
    scoping_data.push_frame()
    scoping_data.push_scope(arguments_scope)
    out = self.call_handler(self.code)
    scoping_data.pop_scope()
    scoping_data.pop_frame()
    return out
 

