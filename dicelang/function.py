import copy
import lark
from dicelang import decompiler
from dicelang import grammar
from dicelang.exceptions import DefinitionError, CallError

class Function(object):
  parser = lark.Lark(grammar.raw_text, start='function', parser='earley')
  
  @staticmethod
  def use_serializable_function_repr(yes_if_true):
    if yes_if_true:
      Function.__repr__ = Function.file_repr
    else:
      Function.__repr__ = Function.normal_repr
  
  def __init__(self, tree_or_source, param_names=None, closed_vars=None):
    self.visitor = None
    self.dcmp = decompiler.Decompiler()
    self.closed = closed_vars if closed_vars else [{}]
    if param_names is None:
      tree = Function.parser.parse(tree_or_source)
      self.code = tree.children[-1]
      self.params = Function._normalize_params(tree.children[0:-1])
      param_string = ', '.join(self.params)
      self.src = f'{self.dcmp.decompile(tree)}'
    else:
      Function._ensure_unique(param_names)
      self.code = tree_or_source
      self.params = Function._normalize_params(param_names)
      param_string = ', '.join(param_names)
      self.src = f'({param_string}) -> {self.dcmp.decompile(tree_or_source)}'
  
  def __deepcopy__(self, memodict={}):
    newtree = type(self.code)(
      copy.deepcopy(self.code.data),
      copy.deepcopy(self.code.children))
    return type(self)(newtree, self.params[:], copy.deepcopy(self.closed))
  
  @staticmethod
  def _ensure_unique(parameters):
    parameters = sorted(parameters)
    last = None
    for parameter in parameters:
      if parameter == last:
        raise DefinitionError(f'Parameter name duplicated: "{parameter}".')
      last = parameter
    return True
  
  @staticmethod
  def _normalize_params(parameters):
    out = []
    for param in parameters:
      out.append(str(param))
    return out
  
  def normal_repr(self):
    return f'{self.src}'
  
  def file_repr(self):
    flat_source = self.src.replace('\n', '\f')
    return f'Function({flat_source!r}, closed_vars={self.closed!r})'
    
  __repr__ = normal_repr
  
  def __call__(self, scoping_data, visitor, *args):
    if self.visitor is None:
      self.visitor = visitor
    if len(self.params) != len(args):
      raise CallError('Arguments mismatch formal parameters in length.')
    
    arguments_scope = dict(zip(self.params, args))
    scoping_data.push_frame()
    scoping_data.push_scope(arguments_scope)
    scoping_data.push_closure(self.closed)
    out = self.visitor.walk(
      self.code,
      scoping_data.user,
      scoping_data.server,
      scoping_data)
    scoping_data.pop_closure()
    scoping_data.pop_scope()
    scoping_data.pop_frame()
    
    return out
 

