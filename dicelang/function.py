import lark

class SyntaxToken(object):
  def __init__(self, lark_token):
    self.type = lark_token.type
    self.value = lark_token.value
  
  def __repr__(self):
    return 'SyntaxToken({}, {})'.format(repr(self.type), repr(self.value))

class SyntaxTree(object):
  def __init__(self, lark_tree):
    self.data = lark_tree.data
    self.children = [ ]
    for child in lark_tree.children:
      if isinstance(child, (lark.Token, SyntaxToken)):
        self.children.append(SyntaxToken(child))
      else:
        self.children.append(SyntaxTree(child))
  
  def __repr__(self):
    return 'SyntaxTree({}, {})'.format(repr(self.data), repr(self.children))

class Function(object):
  def __init__(self, call_handler, lark_tree, *param_names):
    self.code = SyntaxTree(lark_tree)
    self.params = param_names
    self.call_handler = call_handler
  
  def __repr__(self):
    return 'Function({}, {})'.format(repr(self.code), repr(self.params))
  
  def __str__(self):
    return '<Function object with {} arguments>'.format(len(self.params))

  def __call__(self, scoping_data, *args):
    if len(self.params) != len(args):
      raise FunctionCallException(FunctionCallException.length_error)
    arguments_scope = dict(zip(self.params, args))
    scoping_data.push_frame()
    scoping_data.push_scope(arguments_scope)
    out = self.call_handler(self.code)
    scoping_data.pop_scope()
    scoping_data.pop_frame()
    return out
 
class FunctionCallException(Exception):
  length_error = 'Function formal parameters mismatch arguments in length.'
  pass
 

