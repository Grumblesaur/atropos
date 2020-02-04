import lark
from dicelang.bridge import get_function_call_handler

class FunctionCallException(Exception):
  pass

length_error = FunctionCallException(
  'Function formal parameters mismatch arguments in length.')
 
class SyntaxToken(object):
  @staticmethod
  def make(lark_token):
    return SyntaxToken(lark_token.type, lark_token.value)
  
  def __init__(self, token_type, token_value):
    self.type = token_type
    self.value = token_value
  
  def __repr__(self):
    return 'SyntaxToken({}, {})'.format(repr(self.type), repr(self.value))

class SyntaxTree(object):
  @staticmethod
  def make(lark_tree):
    return SyntaxTree(lark_tree.data, lark_tree.children)
  
  def __init__(self, tree_data, tree_children):
    self.data = tree_data
    self.children = []
    for child in tree_children:
      if isinstance(child, lark.Token):
        out = SyntaxToken.make(child)
      elif isinstance(child, SyntaxToken):
        out = SyntaxToken(child.type, child.value)
      elif isinstance(child, lark.Tree):
        out = SyntaxTree.make(child)
      elif isinstance(child, SyntaxTree):
        out = SyntaxTree(child.data, child.children)
      self.children.append(out)
  
  def __repr__(self):
    return 'SyntaxTree({}, {})'.format(repr(self.data), repr(self.children))

class Function(object):
  @staticmethod
  def make(lark_tree, param_names):
    return Function(SyntaxTree.make(lark_tree), param_names)
  
  def __init__(self, syntax_tree, param_names):
    self.code = syntax_tree
    self.params = param_names
    self.call_handler = get_function_call_handler()
  
  def __repr__(self):
    return 'Function({}, {})'.format(repr(self.code), repr(self.params))
  
  def __str__(self):
    return '<Function object with {} arguments>'.format(len(self.params))

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
 


