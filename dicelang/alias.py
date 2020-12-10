from dicelang.function import Function
from dicelang.exceptions import AliasError

class Alias(object):
  def __init__(self, aliased_function):
    if len(aliased_function.params) > 0:
      raise AliasError('Aliased function must have exactly 0 parameters.')
    self.aliased = aliased_function
    
  def __repr__(self):
    with Function.SerializableRepr() as _:
      out = f'Alias({self.aliased!r})'
    return out
  
  def __call__(self, scoping_data, visitor):
    return self.aliased(scoping_data, visitor)

