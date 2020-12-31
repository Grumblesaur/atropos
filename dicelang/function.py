import copy
import lark
from dicelang import decompiler
from dicelang import grammar
from dicelang.undefined import Undefined
from dicelang.exceptions import DefinitionError, CallError

class Function(object):
  parser = lark.Lark(grammar.raw_text, start='function', parser='earley')
  deparser = decompiler.Decompiler()
  
  class SerializableRepr:
    def __init__(self):
      pass
    def __enter__(self):
      Function.__repr__ = Function.serializable_repr
    def __exit__(self, *args):
      Function.__repr__ = Function.repl_repr
  
  def __init__(self, tree_or_src, param_names=None, closed_vars=None):
    if param_names is None:
      tree = self.parse(tree_or_src)
      self.code = tree.children[-1]
      self.params = tree.children[0:-1]
      self.src = self.decompile(tree)
    else:
      self.code = tree_or_src
      self.params = param_names
      signature, body = ', '.join(param_names), self.decompile(tree_or_src)
      self.src = f'({signature}) -> {body}'
    
    self.normalize()
    self.visitor = None
    self.closed = closed_vars if closed_vars else [{}]
    self.this = Undefined
  
  def __deepcopy__(self, memodict={}):
    '''Override __deepcopy__ to prevent bugs when function objects are moved
    or deleted by users.'''
    newtree = type(self.code)(
      copy.deepcopy(self.code.data),
      copy.deepcopy(self.code.children))
    return type(self)(newtree, self.params[:], copy.deepcopy(self.closed))
  
  def normalize(self):
    '''Ensure that all parameters are strings and not Lark Tokens, then check
    for duplicated parameter names. If a parameter name is duplicated, raise
    an error indicating which.'''
    normalized_params = []
    for param in self.params:
      normalized_params.append(str(param))
    last = None
    for param in sorted(normalized_params):
      if param == last:
        raise DefinitionError(f'Parameter name duplicated: "{param}".')
      last = param
    self.params = normalized_params
  
  def parse(self, src):
    '''Proxy method for parsing a function source string.'''
    return Function.parser.parse(src)
  
  def decompile(self, tree):
    '''Proxy method for decompiling a function source tree.'''
    return Function.deparser.decompile(tree)
  
  def repl_repr(self):
    '''The representation shown to users of the language.'''
    return f'{self.src}'
  
  def serializable_repr(self):
    '''The representation used for serializing function objects.'''
    flat_source = self.src.replace('\n', '\f')
    return f'Function({flat_source!r}, closed_vars={self.closed!r})'
    
  __repr__ = repl_repr
  
  def __eq__(self, other):
    if not isinstance(other, Function):
      return False
    return self.params == other.params and self.code == other.code
  
  def __call__(self, visitor, *args):
    if self.visitor is None:
      self.visitor = visitor
    if len(self.params) != len(args):
      raise CallError('Arguments mismatch formal parameters in length.')
    
    arguments_scope = dict(zip(self.params, args))
    arguments_scope['this'] = self.this
    scoping_data = self.visitor.scoping_data
    
    scoping_data.push_function_call(arguments_scope, self.closed)
    out = self.visitor.walk(self.code, scoping_data)
    scoping_data.pop_function_call()
    self.this = Undefined
    return out
 

