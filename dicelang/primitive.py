import copy
import lark
from dicelang import decompiler
from dicelang import grammar

class Primitive(object):
  parser = lark.Lark(grammar.raw_text, start='primitive', parser='earley')
  dcmp = decompiler.Decompiler()
  
  def __init__(self, tree_or_src, closed_vars=None):
    self.visitor = None
    self.closed = closed_vars if closed_vars else [{}]
    
    if isinstance(tree_or_src, str):
      self.code = Primitive.parser.parse(tree_or_src)
      self.src  = tree_or_src
    else:
      self.code = tree_or_src
      self.src = f'do {Primitive.dcmp.decompile(tree_or_src)}'
  
  def __deepcpy__(self, memodict={}):
    newtree = type(self.code)(
      copy.deepcopy(self.code.data),
      copy.deepcopy(self.code.children))
    return type(self)(newtree)
  
  def normal_repr(self):
    return f'{self.src}'
  
  __repr__ = normal_repr
  
  def file_repr(self):
    flat_source = self.src.replace('\n', '\f')
    return f'Primitive({flat_source!r}, closed_vars={self.closed!r})'
  
  def __call__(self, scoping_data, visitor):
    if self.visitor is None:
      self.visitor = visitor
    scoping_data.push_frame()
    scoping_data.push_scope()
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

  @staticmethod
  def use_serializable_repr(arg=True):
    Primitive.__repr__ = Primitive.file_repr if arg else Primitive.normal_repr

