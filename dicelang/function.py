import lark
from dicelang import decompiler
from dicelang import grammar
from dicelang import visitor

class FunctionCallException(Exception):
  pass

length_error = FunctionCallException(
  'Function formal parameters mismatch arguments in length.')
 
class Function(object):
  parser = lark.Lark(grammar.raw_text, start='function', parser='earley')
  
  @staticmethod
  def use_serializable_function_repr(yes_if_true):
    if yes_if_true:
      Function.__repr__ = Function.file_repr
    else:
      Function.__repr__ = Function.normal_repr
  
  def __init__(self, tree_or_source, param_names=None):
    self.visitor = None
    self.decompiler = decompiler.Decompiler()
    if param_names is None:
      self.source = tree_or_source
      tree = Function.parser.parse(tree_or_source)
      self.code = tree.children[-1]
      self.params = tree.children[0:-1]
    else:
      self.code = tree_or_source
      self.params = param_names
      param_string = ', '.join(param_names)
      self.source = f'({param_string}) -> {decompile(tree_or_source)}'
  
  def normal_repr(self):
    return f'{self.source}'
  
  def file_repr(self):
    flat_source = self.source.replace('\n', ' ')
    flat_source = flat_source.replace('\t', ' ')
    return f'Function({flat_source!r})'

  __repr__ = normal_repr
  
  def __call__(self, scoping_data, visitor, *args):
    if self.visitor is None:
      self.visitor = visitor
    if len(self.params) != len(args):
      raise length_error
    arguments_scope = dict(zip(self.params, args))
    scoping_data.push_frame()
    scoping_data.push_scope(arguments_scope)
    out = self.call_handler(self.code)
    scoping_data.pop_scope()
    scoping_data.pop_frame()
    return out
 

